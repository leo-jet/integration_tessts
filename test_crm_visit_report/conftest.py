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
from fixtures.apps import app_loader


def _get_crm_apps_role_priority_app() -> List[Dict[str, Any]]:
    """
    Retourne les applications avec role_priority='app' autorisées pour CRM.
    
    Returns:
        Liste des apps avec le rôle crm_visit_report et role_priority='app'
    """
    return app_loader.filter_apps(role="crm_visit_report", role_priority="app")


@pytest.fixture(scope="module")
def crm_apps_role_priority_app() -> List[Dict[str, Any]]:
    """
    Retourne les applications avec role_priority='app' autorisées pour CRM.
    
    Returns:
        Liste des apps avec le rôle crm_visit_report et role_priority='app'
    """
    apps = _get_crm_apps_role_priority_app()
    
    if not apps:
        pytest.skip("No apps found with role='crm_visit_report' and role_priority='app'")
    
    return apps


def pytest_generate_tests(metafunc):
    """
    Génère dynamiquement les paramètres de test pour toutes les apps autorisées.
    Permet de tester chaque app individuellement avec un ID de test clair.
    """
    if "crm_app_authorized" in metafunc.fixturenames:
        apps = _get_crm_apps_role_priority_app()
        
        if apps:
            # Paramétrer le test avec toutes les apps, en utilisant app_name comme ID
            metafunc.parametrize(
                "crm_app_authorized",
                apps,
                ids=[app.get("app_name", f"app_{i}") for i, app in enumerate(apps)]
            )
        else:
            # Si aucune app, paramétrer avec un skip
            metafunc.parametrize(
                "crm_app_authorized", 
                [pytest.param(None, marks=pytest.mark.skip(reason="No apps found with role='crm_visit_report' and role_priority='app'"))]
            )


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
