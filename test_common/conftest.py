"""
Fixtures spécifiques pour les tests des endpoints Common (fetch_history).

Ces fixtures sont génériques et peuvent être adaptées à différentes
implémentations d'API avec gestion de l'historique de conversations.
"""
import pytest
from typing import List, Dict, Any
from fixtures.schemas import (
    ChatItemSchema,
    LoadPreviousChatResponseSchema,
    ErrorResponseSchema
)


@pytest.fixture(scope="module")
def common_apps_with_fetch_history(filter_apps_by) -> List[Dict[str, Any]]:
    """
    Retourne les applications avec fetch_history=1.
    
    Returns:
        Liste des apps avec fetch_history activé
    """
    apps = filter_apps_by(custom_filter=lambda app: app.get("fetch_history") == 1)
    
    if not apps:
        pytest.skip("No apps found with fetch_history=1")
    
    return apps


@pytest.fixture
def common_app_authorized(common_apps_with_fetch_history) -> Dict[str, Any]:
    """
    Retourne une application autorisée pour les endpoints common (première trouvée).
    
    Returns:
        Dict représentant une app autorisée avec fetch_history
    """
    return common_apps_with_fetch_history[0]


@pytest.fixture
def chat_item_schema() -> ChatItemSchema:
    """Schéma de validation pour un élément de chat."""
    return ChatItemSchema()


@pytest.fixture
def load_previous_chat_schema() -> LoadPreviousChatResponseSchema:
    """Schéma de validation pour la réponse de load_previous_chat."""
    return LoadPreviousChatResponseSchema()


@pytest.fixture
def error_response_schema() -> ErrorResponseSchema:
    """Schéma de validation pour les réponses d'erreur."""
    return ErrorResponseSchema()


@pytest.fixture(scope="module")
def common_apps_without_fetch_history(filter_apps_by) -> List[Dict[str, Any]]:
    """
    Retourne les applications SANS fetch_history.
    
    Returns:
        Liste des apps avec fetch_history=0 ou non défini
    """
    apps = filter_apps_by(custom_filter=lambda app: app.get("fetch_history", 0) == 0)
    
    if not apps:
        pytest.skip("No apps found without fetch_history")
    
    return apps


@pytest.fixture
def common_app_unauthorized(common_apps_without_fetch_history) -> Dict[str, Any]:
    """
    Retourne une application NON autorisée pour les endpoints fetch_history.
    
    Returns:
        Dict représentant une app sans fetch_history
    """
    return common_apps_without_fetch_history[0]


@pytest.fixture
def test_chat_id() -> str:
    """
    ID d'un chat existant pour les tests (doit exister dans le système).
    
    Note: Vous devrez peut-être adapter cette valeur pour qu'elle corresponde
    à un chat_id réel dans votre environnement de test.
    """
    return "test_chat_for_history_001"
