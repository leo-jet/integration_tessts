"""
Fixtures spécifiques pour les tests Chatbot Expert.

L'endpoint /get_chatbot_expert_answer permet d'obtenir une réponse streamée
du chatbot expert sur les produits.

Endpoint: POST /get_chatbot_expert_answer
Content-Type: multipart/form-data
Response: text/event-stream (SSE)
"""
import pytest
from typing import List, Dict, Any


@pytest.fixture(scope="module")
def chatbot_expert_apps_role_priority_app(filter_apps_by) -> List[Dict[str, Any]]:
    """
    Retourne les applications avec role_priority='app' autorisées pour Chatbot Expert.
    
    L'endpoint /get_chatbot_expert_answer utilise le décorateur check_access,
    donc nécessite des apps avec le rôle approprié.
    
    Returns:
        Liste des apps avec le rôle chatbot_expert et role_priority='app'
    """
    apps = filter_apps_by(role="chatbot_expert", role_priority="app")
    
    if not apps:
        pytest.skip("No apps found with role='chatbot_expert' and role_priority='app'")
    
    return apps


@pytest.fixture
def chatbot_expert_app_authorized(chatbot_expert_apps_role_priority_app) -> Dict[str, Any]:
    """
    Retourne une application autorisée pour Chatbot Expert (première trouvée).
    
    Returns:
        Dict représentant une app autorisée
    """
    return chatbot_expert_apps_role_priority_app[0]


@pytest.fixture
def valid_chatbot_expert_data(get_chat_id, chatbot_expert_app_authorized) -> Dict[str, str]:
    """
    Données valides pour une requête Chatbot Expert.
    
    Returns:
        Dict avec tous les champs requis
    """
    chat_id = get_chat_id(app=chatbot_expert_app_authorized)
    return {
        "chat_id": chat_id,
        "user_question": "je cherche un spot LED pour ma salle de bain?"
    }


@pytest.fixture
def chatbot_expert_test_questions() -> List[str]:
    """
    Liste de questions de test pour le chatbot expert.
    
    Returns:
        Liste de questions variées pour tester différents scénarios
    """
    return [
        "je cherche un spot LED pour ma salle de bain?",
        "Quel câble électrique pour une installation extérieure?",
        "Recommandez-moi un disjoncteur différentiel 30mA",
        "Quelle est la différence entre un câble H07V-U et H07V-R?",
        "Je cherche une prise étanche IP65"
    ]
