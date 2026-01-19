"""
Configuration pour les tests d'intégration.

Configuration centralisée et agnostique qui charge les paramètres
depuis les variables d'environnement (.env file).
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration centralisée pour les tests."""
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Azure OAuth Configuration
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    
    # OAuth2 Token URL
    @classmethod
    def get_token_url(cls) -> str:
        """Retourne l'URL pour obtenir le token OAuth2."""
        return f"https://login.microsoftonline.com/{cls.AZURE_TENANT_ID}/oauth2/v2.0/token"
    
    # Retry Configuration
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_BACKOFF_FACTOR: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
    RETRY_INITIAL_DELAY: float = float(os.getenv("RETRY_INITIAL_DELAY", "1.0"))
    
    @classmethod
    def validate(cls) -> None:
        """Valide que toutes les configurations requises sont présentes."""
        if not cls.AZURE_TENANT_ID:
            raise ValueError("AZURE_TENANT_ID is required in .env file")
        if not cls.API_BASE_URL:
            raise ValueError("API_BASE_URL is required in .env file")


# Valider la configuration au chargement
Config.validate()
