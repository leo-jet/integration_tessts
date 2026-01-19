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
        
        Args:
            app: Dictionnaire contenant oauth_config avec client_id_env_var et client_secret_env_var
            
        Returns:
            str: Access token valide
            
        Raises:
            AuthenticationError: Si l'authentification échoue
        """
        oauth_config = app.get("oauth_config", {})
        
        # Récupérer les variables d'environnement
        client_id_env = oauth_config.get("client_id_env_var")
        client_secret_env = oauth_config.get("client_secret_env_var")
        tenant_id = oauth_config.get("tenant_id")
        scope = oauth_config.get("scope")
        
        if not all([client_id_env, client_secret_env, tenant_id, scope]):
            raise AuthenticationError(
                f"Missing OAuth config for app {app.get('app_name')}"
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
