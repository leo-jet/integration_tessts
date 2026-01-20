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
    
    # Azure OAuth Configuration (optionnel si tenant_id est dans apps.json)
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    
    # Mock Authentication Configuration
    # Set MOCK_AUTH=true to bypass real authentication and use a mock token
    MOCK_AUTH: bool = os.getenv("MOCK_AUTH", "false").lower() in ("true", "1", "yes")
    # Token to use when MOCK_AUTH is enabled (defaults to a placeholder)
    MOCK_TOKEN: str = os.getenv("MOCK_TOKEN", "mock-token-for-testing")
    
    # Retry Configuration
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_BACKOFF_FACTOR: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
    RETRY_INITIAL_DELAY: float = float(os.getenv("RETRY_INITIAL_DELAY", "1.0"))
    
    @classmethod
    def validate(cls) -> None:
        """Valide que toutes les configurations requises sont présentes."""
        if not cls.API_BASE_URL:
            raise ValueError("API_BASE_URL is required in .env file")
        # Note: AZURE_TENANT_ID est optionnel si spécifié dans oauth_config de chaque app


# Valider la configuration au chargement
Config.validate()
