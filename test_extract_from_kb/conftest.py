"""
Fixtures spécifiques pour les tests extract_from_knowledge_base.

L'endpoint extract_from_knowledge_base permet d'extraire des informations 
depuis une knowledge base spécifiée et retourne une réponse en streaming SSE.
"""
import pytest
from typing import List, Dict, Any
import uuid


@pytest.fixture(scope="module")
def kb_apps(apps) -> List[Dict[str, Any]]:
    """
    Retourne toutes les applications qui ont des tests KB configurés dans roles_test.
    
    Un test KB est identifié par la présence de 'kb_id' dans la config du role.
    
    Returns:
        List[Dict]: Liste des applications avec au moins un test KB
    """
    kb_apps_list = []
    
    for app in apps:
        roles_test = app.get("roles_test", {})
        
        # Vérifier si au moins un rôle a un kb_id (= test KB)
        has_kb_test = any(
            "kb_id" in test_config 
            for test_config in roles_test.values()
        )
        
        if has_kb_test:
            kb_apps_list.append(app)
    
    if not kb_apps_list:
        pytest.skip(
            "No apps with KB tests configured. "
            "Please add a role with 'kb_id' in roles_test in data/apps.json"
        )
    
    return kb_apps_list


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
    pour tous les rôles qui ont un kb_id dans leur config de test.
    
    Returns:
        List[tuple]: [(app, role_name, config), ...]
    """
    test_configs = []
    
    for app in kb_apps:
        roles_test = app.get("roles_test", {})
        
        # Parcourir tous les rôles avec config de test
        for role_name, test_config in roles_test.items():
            # Si la config a un kb_id, c'est un test KB
            if "kb_id" in test_config:
                test_configs.append((app, role_name, test_config))
    
    if not test_configs:
        pytest.skip("No KB roles with test configuration (kb_id) found")
    
    return test_configs

