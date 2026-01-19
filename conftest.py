"""
Configuration globale et fixtures partagées pour tous les tests d'intégration.

Architecture modulaire et agnostique réutilisable pour tester n'importe
quelle API REST avec authentification OAuth2.
"""
import pytest
from typing import List, Dict, Any, Callable

from fixtures.config import Config
from fixtures.apps import app_loader
from fixtures.api_client import APIClient


# ============================================================================
# Fixtures de configuration
# ============================================================================

@pytest.fixture(scope="session")
def config() -> Config:
    """Retourne la configuration globale."""
    return Config


@pytest.fixture(scope="session")
def base_url(config: Config) -> str:
    """URL de base de l'API."""
    return config.API_BASE_URL


# ============================================================================
# Fixtures pour le chargement des apps
# ============================================================================

@pytest.fixture(scope="session")
def apps() -> List[Dict[str, Any]]:
    """
    Charge toutes les applications depuis apps.json.
    
    Returns:
        Liste de toutes les applications validées
    """
    return app_loader.load_apps()


@pytest.fixture
def filter_apps_by(apps: List[Dict[str, Any]]) -> Callable:
    """
    Factory fixture pour filtrer les applications.
    
    Usage:
        def test_something(filter_apps_by):
            crm_apps = filter_apps_by(role="crm_visit_report", role_priority="app")
    
    Returns:
        Fonction de filtrage
    """
    def _filter(
        role: str = None,
        role_priority: str = None,
        country: str = None,
        custom_filter: Callable[[Dict[str, Any]], bool] = None
    ) -> List[Dict[str, Any]]:
        return app_loader.filter_apps(
            role=role,
            role_priority=role_priority,
            country=country,
            custom_filter=custom_filter
        )
    
    return _filter


# ============================================================================
# Fixtures pour le client API
# ============================================================================

@pytest.fixture
def api_client(base_url: str) -> APIClient:
    """
    Client API pour effectuer les requêtes HTTP.
    
    Returns:
        Instance de APIClient configurée
    """
    return APIClient(base_url=base_url)


# ============================================================================
# Fixtures utilitaires
# ============================================================================

@pytest.fixture
def chat_id() -> str:
    """ID de chat par défaut pour les tests."""
    return "test_chat_integration_12345"
