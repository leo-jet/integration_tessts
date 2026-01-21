"""
Tests de scénario métier pour l'endpoint /get_chatbot_expert_answer.

L'endpoint /get_chatbot_expert_answer permet aux commerciaux de poser des questions
sur les produits et retourne une réponse en streaming SSE.

Endpoint: POST /get_chatbot_expert_answer
Content-Type: multipart/form-data
Response: text/event-stream (SSE)

Décorateurs:
- check_access: Vérifie les droits d'accès
- conditional_route: Routage conditionnel

Paramètres requis:
- chat_id (string): L'identifiant du chat
- user_question (string): La question de l'utilisateur

Paramètres optionnels:
- audio (binary): Fichier audio à uploader
"""
import pytest
import json
from typing import Dict, Any


class TestChatbotExpertBusinessScenario:
    """Tests du scénario métier complet pour Chatbot Expert."""
    
    def test_chatbot_expert_streaming_response(
        self,
        api_client,
        chatbot_expert_app_authorized: Dict[str, Any],
        valid_chatbot_expert_data: Dict[str, str]
    ):
        """
        Test du scénario métier complet pour une question au chatbot expert.
        
        Ce test valide :
        1. L'authentification OAuth2 avec l'application
        2. L'appel à l'endpoint avec des données valides
        3. Le code de réponse HTTP 200
        4. Le Content-Type text/event-stream
        5. Le format SSE valide (data: {...})
        6. La structure des événements (role, content)
        
        Scénario métier :
        - Un commercial pose une question sur un produit
        - Le système retourne une réponse en streaming SSE
        - La réponse contient des informations produit pertinentes
        
        Expected : 200 OK avec streaming SSE valide
        """
        # ============================================
        # GIVEN : Question utilisateur sur les produits
        # ============================================
        endpoint = "/get_chatbot_expert_answer"
        
        # ============================================
        # WHEN : Appel à l'endpoint en streaming
        # ============================================
        response = api_client.post(
            endpoint=endpoint,
            app=chatbot_expert_app_authorized,
            data=valid_chatbot_expert_data,
            stream=True
        )
        
        # ============================================
        # THEN : Validation de la réponse streaming
        # ============================================
        
        # 1. Vérifier le code HTTP
        assert response.status_code == 200, (
            f"Expected HTTP 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # 2. Vérifier le Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "text/event-stream" in content_type, (
            f"Expected Content-Type 'text/event-stream', got '{content_type}'"
        )
        
        # 3. Lire et valider les événements SSE
        events = []
        content_parts = []
        
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data:"):
                # Extraire le JSON après "data: "
                json_str = line[5:].strip()
                if json_str:
                    try:
                        event_data = json.loads(json_str)
                        events.append(event_data)
                        
                        # Collecter le contenu
                        if "content" in event_data:
                            content_parts.append(event_data["content"])
                    except json.JSONDecodeError:
                        # Certains événements peuvent ne pas être du JSON valide
                        pass
        
        # 4. Vérifier qu'on a reçu des événements
        assert len(events) > 0, "No SSE events received"
        
        # 5. Vérifier la structure des événements
        for i, event in enumerate(events):
            # Les événements doivent avoir un role ou un content
            has_role = "role" in event
            has_content = "content" in event
            assert has_role or has_content, (
                f"Event {i} should have 'role' or 'content': {event}"
            )
        
        # 6. Vérifier qu'on a du contenu
        full_content = "".join(content_parts)
        assert len(full_content) > 0, "Response content should not be empty"
        
        # 7. Log pour debug
        print(f"\n✅ Chatbot Expert streaming test passed")
        print(f"   - Events received: {len(events)}")
        print(f"   - Content length: {len(full_content)} chars")
        print(f"   - First 200 chars: {full_content[:200]}...")


class TestChatbotExpertValidation:
    """Tests de validation des paramètres pour Chatbot Expert."""
    
    def test_chatbot_expert_missing_user_question(
        self,
        api_client,
        chatbot_expert_app_authorized: Dict[str, Any],
        get_chat_id
    ):
        """
        Test avec user_question manquant.
        
        Expected : 400 Bad Request avec message d'erreur
        """
        endpoint = "/get_chatbot_expert_answer"
        chat_id = get_chat_id(app=chatbot_expert_app_authorized)
        
        # Données avec user_question manquant
        data = {
            "chat_id": chat_id
            # user_question manquant
        }
        
        response = api_client.post(
            endpoint=endpoint,
            app=chatbot_expert_app_authorized,
            data=data
        )
        
        assert response.status_code == 400, (
            f"Expected HTTP 400, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # Vérifier le format de l'erreur
        try:
            error_data = response.json()
            assert "errors" in error_data or "error" in error_data or "message" in error_data, (
                f"Error response should contain 'errors', 'error' or 'message': {error_data}"
            )
        except json.JSONDecodeError:
            # Acceptable si le message d'erreur n'est pas JSON
            pass
        
        print(f"\n✅ Missing user_question validation test passed")


    def test_chatbot_expert_missing_chat_id(
        self,
        api_client,
        chatbot_expert_app_authorized: Dict[str, Any]
    ):
        """
        Test avec chat_id manquant.
        
        Expected : 400 Bad Request avec message d'erreur
        """
        endpoint = "/get_chatbot_expert_answer"
        
        # Données avec chat_id manquant
        data = {
            "user_question": "je cherche un spot LED?"
            # chat_id manquant
        }
        
        response = api_client.post(
            endpoint=endpoint,
            app=chatbot_expert_app_authorized,
            data=data
        )
        
        assert response.status_code == 400, (
            f"Expected HTTP 400, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        print(f"\n✅ Missing chat_id validation test passed")


    def test_chatbot_expert_empty_user_question(
        self,
        api_client,
        chatbot_expert_app_authorized: Dict[str, Any],
        get_chat_id
    ):
        """
        Test avec user_question vide.
        
        Expected : 400 Bad Request ou comportement défini
        """
        endpoint = "/get_chatbot_expert_answer"
        chat_id = get_chat_id(app=chatbot_expert_app_authorized)
        
        data = {
            "chat_id": chat_id,
            "user_question": ""
        }
        
        response = api_client.post(
            endpoint=endpoint,
            app=chatbot_expert_app_authorized,
            data=data
        )
        
        # Une question vide devrait retourner 400
        assert response.status_code in [400, 200], (
            f"Expected HTTP 400 or 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        print(f"\n✅ Empty user_question test passed (status: {response.status_code})")


class TestChatbotExpertUnauthorized:
    """Tests de sécurité pour Chatbot Expert."""
    
    def test_chatbot_expert_without_auth(
        self,
        chatbot_expert_app_authorized: Dict[str, Any]
    ):
        """
        Test sans authentification.
        
        Note: Ce test nécessite un appel direct sans le client API
        pour éviter l'ajout automatique des headers d'auth.
        
        Expected : 401 Unauthorized
        """
        import requests
        from fixtures.config import Config
        
        endpoint = "/get_chatbot_expert_answer"
        url = f"{Config.API_BASE_URL}{endpoint}"
        
        data = {
            "chat_id": "test-123",
            "user_question": "test question"
        }
        
        # Appel sans headers d'authentification
        response = requests.post(
            url,
            data=data,
            timeout=Config.API_TIMEOUT
        )
        
        assert response.status_code in [401, 403], (
            f"Expected HTTP 401 or 403, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        print(f"\n✅ Unauthorized access test passed (status: {response.status_code})")
