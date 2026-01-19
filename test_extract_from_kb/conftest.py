"""
Fixtures spécifiques pour les tests extract_from_knowledge_base.

L'endpoint extract_from_knowledge_base permet d'extraire des informations 
depuis une knowledge base spécifiée et retourne une réponse en streaming SSE.
"""
import pytest
from typing import List, Dict, Any


@pytest.fixture(scope="module")
def kb_apps(filter_apps_by) -> List[Dict[str, Any]]:
    """
    Retourne toutes les applications configurées pour la knowledge base.
    
    Returns:
        List[Dict]: Liste des applications avec rôle 'knowledge_base'
    """
    apps = filter_apps_by(lambda app: "knowledge_base" in app.get("roles", []))
    
    if not apps:
        pytest.skip("No apps with 'knowledge_base' role configured")
    
    return apps


@pytest.fixture(scope="module")
def kb_app(kb_apps) -> Dict[str, Any]:
    """
    Retourne la première application knowledge_base disponible.
    
    Returns:
        Dict: Configuration de l'application
    """
    return kb_apps[0]


@pytest.fixture(scope="module")
def kb_roles_with_tests(kb_apps) -> List[tuple]:
    """
    Retourne une liste de tuples (app, role_name, role_test_config)
    pour tous les rôles knowledge_base qui ont une config de test.
    
    Returns:
        List[tuple]: [(app, role_name, config), ...]
    """
    test_configs = []
    
    for app in kb_apps:
        roles_test = app.get("roles_test", {})
        
        # Parcourir tous les rôles de l'app
        for role in app.get("roles", []):
            # Si le rôle est lié à KB et a une config de test
            if "knowledge_base" in role.lower() and role in roles_test:
                test_config = roles_test[role]
                test_configs.append((app, role, test_config))
    
    if not test_configs:
        pytest.skip("No knowledge_base roles with test configuration found")
    
    return test_configs

