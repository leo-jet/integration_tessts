"""
Fixtures spécifiques pour les tests CRM Visit Report.

Ces fixtures sont génériques et peuvent être adaptées à différentes
implémentations d'API CRM visit report.
"""
import pytest
from typing import List, Dict, Any
from fixtures.schemas import (
    CrmVisitReportResponseSchema,
    ErrorResponseSchema,
    SUPPORTED_LANGUAGES,
    SUPPORTED_SEGMENTS
)


@pytest.fixture(scope="module")
def crm_apps_role_priority_app(filter_apps_by) -> List[Dict[str, Any]]:
    """
    Retourne les applications avec role_priority='app' autorisées pour CRM.
    
    Returns:
        Liste des apps avec le rôle crm_visit_report et role_priority='app'
    """
    apps = filter_apps_by(role="crm_visit_report", role_priority="app")
    
    if not apps:
        pytest.skip("No apps found with role='crm_visit_report' and role_priority='app'")
    
    return apps


@pytest.fixture
def crm_app_authorized(crm_apps_role_priority_app) -> Dict[str, Any]:
    """
    Retourne une application autorisée pour CRM (première trouvée).
    
    Returns:
        Dict représentant une app autorisée
    """
    return crm_apps_role_priority_app[0]


@pytest.fixture
def crm_response_schema() -> CrmVisitReportResponseSchema:
    """Schéma de validation pour les réponses CRM."""
    return CrmVisitReportResponseSchema()


@pytest.fixture
def error_response_schema() -> ErrorResponseSchema:
    """Schéma de validation pour les réponses d'erreur."""
    return ErrorResponseSchema()


@pytest.fixture
def supported_languages() -> List[str]:
    """Liste des langues supportées."""
    return SUPPORTED_LANGUAGES


@pytest.fixture
def supported_segments() -> List[str]:
    """Liste des segments supportés."""
    return SUPPORTED_SEGMENTS


@pytest.fixture
def valid_crm_data(chat_id: str) -> Dict[str, str]:
    """
    Données valides pour une requête CRM visit report.
    
    Returns:
        Dict avec tous les champs requis
    """
    return {
        "chat_id": chat_id,
        "user_question": "Customer expressed concerns about delivery times, but praised the new digital platform. Follow-up scheduled for next month.",
        "target_lang": "en",
        "client_id": "CLIENT_001",
        "client_segment": "IND"
    }
