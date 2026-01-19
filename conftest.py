"""
Configuration globale et fixtures partagées pour tous les tests d'intégration.

Architecture modulaire et agnostique réutilisable pour tester n'importe
quelle API REST avec authentification OAuth2.
"""
import pytest
import uuid
from typing import List, Dict, Any, Callable

from fixtures.config import Config
from fixtures.apps import app_loader
from fixtures.api_client import APIClient
from fixtures.schemas import (
    CrmVisitReportResponseSchema,
    ChatItemSchema,
    LoadPreviousChatResponseSchema,
    ErrorResponseSchema
)


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


@pytest.fixture(scope="session")
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

@pytest.fixture(scope="session")
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

@pytest.fixture(scope="function")
def get_chat_id(api_client, apps):
    """
    Génère un nouveau chat_id en appelant l'endpoint get_chat_id_route.
    Retourne une fonction callable qui génère un nouveau chat_id pour chaque appel.
    
    Returns:
        callable: Fonction qui retourne un chat_id en appelant l'API
    """
    def _get_chat_id(app=None):
        """Génère un nouveau chat_id via l'API."""
        # Si aucune app n'est fournie, utiliser la première disponible
        target_app = app or apps[0]
        
        try:
            response = api_client.get(
                endpoint="/get_chat_id",
                app=target_app
            )
            
            if response.status_code == 200:
                chat_id = response.text.strip()
                print(f"   🆔 Generated chat_id: {chat_id}")
                return chat_id
            else:
                # Fallback si l'endpoint n'est pas disponible
                fallback_id = f"test-{uuid.uuid4().hex[:12]}"
                print(f"   ⚠️  get_chat_id returned {response.status_code}, using fallback: {fallback_id}")
                return fallback_id
                
        except Exception as e:
            # Fallback en cas d'erreur
            fallback_id = f"test-{uuid.uuid4().hex[:12]}"
            print(f"   ⚠️  Error calling get_chat_id: {e}, using fallback: {fallback_id}")
            return fallback_id
    
    return _get_chat_id


@pytest.fixture
def chat_id(get_chat_id) -> str:
    """ID de chat dynamique pour les tests (génère un nouveau chat_id via l'API)."""
    return get_chat_id()


# ============================================================================
# Fixtures pour les schémas de validation
# ============================================================================

@pytest.fixture(scope="session")
def crm_visit_report_schema():
    """Schéma de validation pour les réponses CRM visit report."""
    return CrmVisitReportResponseSchema()


@pytest.fixture(scope="session")
def chat_item_schema():
    """Schéma de validation pour les items de chat."""
    return ChatItemSchema()


@pytest.fixture(scope="session")
def load_previous_chat_schema():
    """Schéma de validation pour les réponses load_previous_chat."""
    return LoadPreviousChatResponseSchema()


@pytest.fixture(scope="session")
def error_response_schema():
    """Schéma de validation pour les réponses d'erreur."""
    return ErrorResponseSchema()
