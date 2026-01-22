"""
Authentification OAuth2 pour les tests d'intégration.

Client OAuth2 générique avec gestion du retry, cache et backoff exponentiel.
Compatible avec n'importe quelle implémentation Azure AD OAuth2.
"""
import os
import time
import requests
from typing import Dict, Any, Optional
from .config import Config


class AuthenticationError(Exception):
    """Exception levée en cas d'erreur d'authentification."""
    pass


class OAuth2Client:
    """Client OAuth2 avec gestion du retry et du cache."""
    
    def __init__(self):
        self._token_cache: Dict[str, Dict[str, Any]] = {}
    
    def get_access_token(self, app: Dict[str, Any]) -> str:
        """
        Obtient un access token OAuth2 pour une application.
        
        Supporte trois modes :
        - MOCK_AUTH=true : Retourne un token mock (bypass authentification)
        - role_priority="app" : OAuth2 client credentials flow
        - role_priority="user" : Token MSAL pré-généré ou mock
        
        Args:
            app: Dictionnaire contenant oauth_config et role_priority
            
        Returns:
            str: Access token valide
            
        Raises:
            AuthenticationError: Si l'authentification échoue
        """
        # Mode mock global : bypass toute authentification
        if Config.MOCK_AUTH:
            print(f"🔓 MOCK_AUTH enabled - using mock token for {app.get('app_name', 'unknown')}")
            return Config.MOCK_TOKEN
        
        role_priority = app.get("role_priority", "app")
        oauth_config = app.get("oauth_config", {})
        
        # Mode user : utiliser un token pré-généré via MSAL
        if role_priority == "user":
            return self._get_user_token(app, oauth_config)
        
        # Mode app : OAuth2 client credentials
        return self._get_app_token(app, oauth_config)
    
    def _get_user_token(self, app: Dict[str, Any], oauth_config: Dict[str, Any]) -> str:
        """
        Obtient un token pour une application user (MSAL).
        
        Pour les tests, on utilise un token pré-généré stocké dans une variable d'environnement.
        En production, ce token serait obtenu via MSAL interactive flow.
        
        Args:
            app: Application configuration
            oauth_config: Configuration OAuth
            
        Returns:
            str: Access token
            
        Raises:
            AuthenticationError: Si le token n'est pas disponible
        """
        # Essayer de récupérer un token pré-généré
        user_token_env_var = oauth_config.get("user_token_env_var")
        
        print(f"🔑 [AUTH] App: {app.get('app_name')} | role_priority: user")
        print(f"🔑 [AUTH] Looking for token in env var: {user_token_env_var}")
        
        if user_token_env_var:
            token = os.getenv(user_token_env_var)
            if token:
                token_preview = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else token
                print(f"✅ [AUTH] Token found! Preview: {token_preview}")
                print(f"✅ [AUTH] Token length: {len(token)} chars")
                return token
            else:
                print(f"❌ [AUTH] Env var '{user_token_env_var}' is empty or not set!")
        
        # Fallback: générer un mock token pour les tests
        # En production, vous devriez utiliser MSAL pour obtenir un vrai token
        client_id_env = oauth_config.get("client_id_env_var")
        authority = oauth_config.get("authority")
        
        # Lire l'APIM scope depuis les variables d'environnement
        apim_scope_env = oauth_config.get("apim_scope_env_var", "APIM_SCOPE")
        apim_scope = os.getenv(apim_scope_env, oauth_config.get("scope"))
        
        # Pour les tests, accepter un token mock si configuré
        mock_token_env = "MOCK_USER_TOKEN"
        mock_token = os.getenv(mock_token_env)
        if mock_token:
            print(f"⚠️  Using mock token for user app (role_priority='user')")
            return mock_token
        
        raise AuthenticationError(
            f"No user token available for app {app.get('app_name')}. "
            f"For testing, either:\n"
            f"1. Set {user_token_env_var} with a real MSAL token\n"
            f"2. Set {mock_token_env} with a mock token\n"
            f"3. Generate a token using MSAL with:\n"
            f"   - client_id: {os.getenv(client_id_env, 'N/A')}\n"
            f"   - authority: {authority}\n"
            f"   - apim_scope (from env ${apim_scope_env}): {apim_scope}"
        )
    
    def _get_app_token(self, app: Dict[str, Any], oauth_config: Dict[str, Any]) -> str:
        """
        Obtient un token pour une application app (OAuth2 client credentials).
        
        Args:
            app: Application configuration
            oauth_config: Configuration OAuth
            
        Returns:
            str: Access token
            
        Raises:
            AuthenticationError: Si l'authentification échoue
        """
        
        # Récupérer les variables d'environnement
        client_id_env = oauth_config.get("client_id_env_var")
        client_secret_env = oauth_config.get("client_secret_env_var")
        tenant_id = oauth_config.get("tenant_id")
        scope = oauth_config.get("scope")
        
        if not all([client_id_env, client_secret_env, tenant_id, scope]):
            raise AuthenticationError(
                f"Missing OAuth config for app {app.get('app_name')}. "
                f"Required: client_id_env_var, client_secret_env_var, tenant_id, scope"
            )
        
        client_id = os.getenv(client_id_env)
        client_secret = os.getenv(client_secret_env)
        
        if not all([client_id, client_secret]):
            raise AuthenticationError(
                f"Missing credentials in environment: {client_id_env} or {client_secret_env}"
            )
        
        # Vérifier le cache
        cache_key = f"{client_id}:{scope}"
        if cache_key in self._token_cache:
            cached = self._token_cache[cache_key]
            # Vérifier si le token est encore valide (avec marge de 5 minutes)
            if time.time() < cached["expires_at"] - 300:
                return cached["access_token"]
        
        # Obtenir un nouveau token
        token_data = self._request_token(client_id, client_secret, tenant_id, scope)
        
        # Mettre en cache
        self._token_cache[cache_key] = {
            "access_token": token_data["access_token"],
            "expires_at": time.time() + token_data.get("expires_in", 3600)
        }
        
        return token_data["access_token"]
    
    def _request_token(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        scope: str
    ) -> Dict[str, Any]:
        """
        Effectue la requête OAuth2 avec retry et backoff exponentiel.
        
        Args:
            client_id: Client ID de l'application
            client_secret: Client Secret de l'application
            tenant_id: Tenant ID Azure AD
            scope: Scope OAuth2
            
        Returns:
            Dict contenant access_token et expires_in
            
        Raises:
            AuthenticationError: Si toutes les tentatives échouent
        """
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope
        }
        
        last_error = None
        delay = Config.RETRY_INITIAL_DELAY
        
        for attempt in range(Config.RETRY_MAX_ATTEMPTS):
            try:
                response = requests.post(
                    url,
                    data=data,
                    timeout=Config.API_TIMEOUT
                )
                
                if response.status_code == 200:
                    return response.json()
                
                # Erreur serveur (5xx) ou rate limit (429) -> retry
                if response.status_code in [429, 500, 502, 503, 504]:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    if attempt < Config.RETRY_MAX_ATTEMPTS - 1:
                        time.sleep(delay)
                        delay *= Config.RETRY_BACKOFF_FACTOR
                        continue
                
                # Autres erreurs -> fail immédiat
                raise AuthenticationError(
                    f"OAuth2 failed with status {response.status_code}: {response.text}"
                )
                
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if attempt < Config.RETRY_MAX_ATTEMPTS - 1:
                    time.sleep(delay)
                    delay *= Config.RETRY_BACKOFF_FACTOR
                    continue
        
        raise AuthenticationError(
            f"OAuth2 failed after {Config.RETRY_MAX_ATTEMPTS} attempts. Last error: {last_error}"
        )


# Instance globale
oauth2_client = OAuth2Client()
