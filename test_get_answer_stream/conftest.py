"""
Fixtures spécifiques pour les tests get_answer_stream.

L'endpoint get_answer_stream permet d'obtenir une réponse streamée du chatbot
et retourne une réponse en streaming SSE.
"""
import pytest
from typing import List, Dict, Any


@pytest.fixture(scope="module")
def stream_apps(apps) -> List[Dict[str, Any]]:
    """
    Retourne toutes les applications disponibles pour tester le streaming.
    
    Returns:
        List[Dict]: Liste de toutes les applications
    """
    if not apps:
        pytest.skip("No apps configured in apps.json")
    
    return apps


@pytest.fixture(scope="module")
def stream_app(stream_apps) -> Dict[str, Any]:
    """
    Retourne la première application disponible.
    
    Returns:
        Dict: Configuration de l'application
    """
    return stream_apps[0]


@pytest.fixture(scope="module")
def stream_roles_with_tests(stream_apps) -> List[tuple]:
    """
    Retourne une liste de tuples (app, role_name, empty_config)
    pour toutes les applications configurées.
    
    Les tests utilisent une question standard "Bonjour" avec le modèle "gpt-4o".
    
    Returns:
        List[tuple]: [(app, "chatbot", {}), ...]
    """
    test_configs = []
    
    for app in stream_apps:
        # Créer un tuple pour chaque app avec un nom de rôle générique
        test_configs.append((app, "chatbot", {}))
    
    return test_configs
