"""
Client HTTP pour appeler les endpoints API.

Client générique avec authentification OAuth2 automatique,
compatible avec n'importe quelle API REST.
"""
import requests
from typing import Dict, Any, Optional
from .config import Config
from .auth import oauth2_client


class APIClient:
    """Client HTTP pour les appels API avec authentification."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        """
        Initialise le client API.
        
        Args:
            base_url: URL de base de l'API (défaut: Config.API_BASE_URL)
            timeout: Timeout pour les requêtes (défaut: Config.API_TIMEOUT)
        """
        self.base_url = base_url or Config.API_BASE_URL
        self.timeout = timeout or Config.API_TIMEOUT
    
    def _prepare_headers(self, app: Dict[str, Any], extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Prépare les headers pour la requête.
        
        Args:
            app: Application contenant les credentials
            extra_headers: Headers additionnels
            
        Returns:
            Dict avec tous les headers nécessaires
        """
        # Obtenir le token OAuth2
        access_token = oauth2_client.get_access_token(app)
        
        # Log pour debug
        token_preview = f"{access_token[:20]}...{access_token[-10:]}" if len(access_token) > 30 else access_token
        print(f"📤 [REQUEST] Preparing headers for app: {app.get('app_name')}")
        print(f"📤 [REQUEST] Authorization: Bearer {token_preview}")
        print(f"📤 [REQUEST] Ocp-Apim-Subscription-Key: {app['ocp_apim_subscription_key'][:8]}...")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Ocp-Apim-Subscription-Key": app["ocp_apim_subscription_key"]
        }
        
        # En mode MOCK_AUTH, ajouter les headers de simulation
        if Config.MOCK_AUTH:
            # App-Id est ajouté pour toutes les requêtes
            headers["App-Id"] = app.get("app_id", "mock-app-id")
            
            # Unique-Name est ajouté uniquement pour les apps avec role_priority=user
            if app.get("role_priority") == "user":
                headers["Unique-Name"] = app.get("unique_name", "mock-user@example.com")
        
        if extra_headers:
            headers.update(extra_headers)
        
        return headers
    
    def post(
        self,
        endpoint: str,
        app: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False
    ) -> requests.Response:
        """
        Effectue une requête POST.
        
        Args:
            endpoint: Endpoint à appeler (ex: "/crm-visit-report")
            app: Application pour l'authentification
            data: Données du formulaire
            files: Fichiers à uploader
            headers: Headers additionnels
            stream: Si True, retourne une réponse en streaming
            
        Returns:
            Response object de requests
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self._prepare_headers(app, headers)
        
        response = requests.post(
            url,
            headers=request_headers,
            data=data,
            files=files,
            timeout=self.timeout,
            stream=stream
        )
        
        return response
    
    def get(
        self,
        endpoint: str,
        app: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Effectue une requête GET.
        
        Args:
            endpoint: Endpoint à appeler
            app: Application pour l'authentification
            params: Paramètres query string
            headers: Headers additionnels
            
        Returns:
            Response object de requests
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self._prepare_headers(app, headers)
        
        response = requests.get(
            url,
            headers=request_headers,
            params=params,
            timeout=self.timeout
        )
        
        return response
