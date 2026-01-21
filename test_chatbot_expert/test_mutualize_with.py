"""
Tests de mutualisation des chats entre applications (mutualize_with) pour Chatbot Expert.

Ces tests valident que les chats créés par une application via /get_chatbot_expert_answer
peuvent être visibles par une autre application qui a mutualize_with configuré.
"""
import pytest
from typing import Dict, Any, List


class TestChatbotExpertMutualizeWith:
    """Tests de mutualisation des chats entre apps pour Chatbot Expert."""
    
    def test_mutualized_app_can_see_chats_from_chatbot_expert(
        self,
        api_client,
        chatbot_expert_apps_role_priority_app: List[Dict[str, Any]]
    ):
        """
        Test qu'une app mutualisée peut voir les chats créés via chatbot_expert.
        
        Ce test valide :
        1. Création d'un chat avec l'app d'origine via /get_chatbot_expert_answer
        2. Récupération des chats avec l'app mutualisée
        3. Vérification que le chat créé est visible
        
        Scénario métier :
        - Un commercial pose une question sur les produits via l'app A
        - Il bascule ensuite sur l'app B (mutualisée avec A)
        - Il doit pouvoir voir et reprendre ses conversations de A dans B
        
        Expected : Le chat créé par A apparaît dans get_recent_chats de B
        """
        # ============================================
        # GIVEN : Deux apps avec mutualize_with configuré
        # ============================================
        
        # Trouver une paire d'apps avec mutualize_with
        origin_app = None
        mutualized_app = None
        
        for app in chatbot_expert_apps_role_priority_app:
            # mutualize_with = 1 active la mutualisation
            # app_to_mutualize_with contient l'ID de l'app d'origine
            mutualize_with = app.get("mutualize_with")
            app_to_mutualize_with = app.get("app_to_mutualize_with")
            
            if mutualize_with == 1 and app_to_mutualize_with:
                # Cette app est mutualisée, trouver l'app d'origine
                origin_candidates = [
                    a for a in chatbot_expert_apps_role_priority_app
                    if a.get("app_id") == app_to_mutualize_with or
                    str(a.get("app_id")) == str(app_to_mutualize_with)
                ]
                if origin_candidates:
                    origin_app = origin_candidates[0]
                    mutualized_app = app
                    break
        
        if not origin_app or not mutualized_app:
            pytest.skip(
                "No pair of apps found with mutualize_with configured for chatbot_expert. "
                "Add two apps in apps.json where one has mutualize_with=1 and app_to_mutualize_with pointing to another app's app_id."
            )
        
        # ============================================
        # STEP 1 : Créer un nouveau chat avec l'app d'origine
        # ============================================
        
        # 1.1. Obtenir un nouveau chat_id
        get_chat_id_response = api_client.get(
            endpoint="/get_chat_id",
            app=origin_app
        )
        
        assert get_chat_id_response.status_code == 200, (
            f"Failed to get chat_id: {get_chat_id_response.status_code}. "
            f"Response: {get_chat_id_response.text}"
        )
        
        new_chat_id = get_chat_id_response.text.strip()
        assert len(new_chat_id) > 0, "chat_id should not be empty"
        
        print(f"\n{'='*60}")
        print(f"📝 Creating test chat with Chatbot Expert (origin app)")
        print(f"{'='*60}")
        print(f"Origin App ID: {origin_app['app_id']}")
        print(f"New Chat ID: {new_chat_id}")
        
        # 1.2. Envoyer une question via chatbot_expert pour créer le chat
        message_data = {
            "chat_id": new_chat_id,
            "user_question": "je cherche un spot LED pour ma salle de bain - test mutualize"
        }
        
        send_message_response = api_client.post(
            endpoint="/get_chatbot_expert_answer",
            app=origin_app,
            data=message_data,
            stream=True
        )
        
        assert send_message_response.status_code == 200, (
            f"Failed to send message: {send_message_response.status_code}. "
            f"Response: {send_message_response.text}"
        )
        
        # Consommer le stream pour compléter la requête
        chunks_received = 0
        for line in send_message_response.iter_lines():
            if line:
                chunks_received += 1
                if chunks_received >= 3:  # Quelques chunks suffisent
                    break
        
        print(f"✅ Chat created successfully via Chatbot Expert ({chunks_received} chunks received)")
        
        # ============================================
        # STEP 2 : Récupérer les chats avec l'app mutualisée
        # ============================================
        
        print(f"\n{'='*60}")
        print(f"🔍 Checking if mutualized app can see the chat")
        print(f"{'='*60}")
        print(f"Mutualized App ID: {mutualized_app['app_id']}")
        print(f"mutualize_with: {mutualized_app.get('mutualize_with')}")
        print(f"app_to_mutualize_with: {mutualized_app.get('app_to_mutualize_with')}")
        
        get_recent_chats_response = api_client.get(
            endpoint="/get_recent_chats",
            app=mutualized_app
        )
        
        assert get_recent_chats_response.status_code == 200, (
            f"Failed to get recent chats: {get_recent_chats_response.status_code}. "
            f"Response: {get_recent_chats_response.text}"
        )
        
        # ============================================
        # STEP 3 : Vérifier que le chat créé est visible
        # ============================================
        
        try:
            chats = get_recent_chats_response.json()
        except Exception as e:
            pytest.fail(f"Failed to parse JSON: {e}. Response: {get_recent_chats_response.text}")
        
        assert isinstance(chats, list), f"Expected list, got {type(chats)}"
        
        # Chercher le chat créé dans la liste
        chat_found = False
        for chat in chats:
            if chat.get("chat_id") == new_chat_id:
                chat_found = True
                print(f"\n✅ Chat found in mutualized app!")
                print(f"  Chat ID: {chat.get('chat_id')}")
                print(f"  Chat Title: {chat.get('chat_title', 'N/A')}")
                break
        
        assert chat_found, (
            f"Chat {new_chat_id} created by Chatbot Expert origin app was NOT found in mutualized app's recent chats. "
            f"This indicates mutualize_with is not working correctly. "
            f"Found {len(chats)} chats in mutualized app."
        )
        
        print(f"\n{'='*60}")
        print(f"✅ Chatbot Expert Mutualize With Test PASSED")
        print(f"{'='*60}")
        print(f"Origin App: {origin_app.get('app_name', origin_app['app_id'])}")
        print(f"Mutualized App: {mutualized_app.get('app_name', mutualized_app['app_id'])}")
        print(f"Test Chat ID: {new_chat_id}")
        print(f"Status: Chat successfully shared between apps")
        print(f"{'='*60}\n")


    def test_load_previous_chat_from_mutualized_chatbot_expert(
        self,
        api_client,
        chatbot_expert_apps_role_priority_app: List[Dict[str, Any]]
    ):
        """
        Test qu'une app mutualisée peut charger un chat créé par chatbot_expert.
        
        Ce test valide :
        1. Création d'un chat via /get_chatbot_expert_answer avec l'app d'origine
        2. Chargement du chat via /load_previous_chat avec l'app mutualisée
        3. Vérification du contenu du chat
        
        Expected : Le contenu du chat est accessible depuis l'app mutualisée
        """
        # Trouver une paire d'apps avec mutualize_with
        origin_app = None
        mutualized_app = None
        
        for app in chatbot_expert_apps_role_priority_app:
            mutualize_with = app.get("mutualize_with")
            app_to_mutualize_with = app.get("app_to_mutualize_with")
            
            if mutualize_with == 1 and app_to_mutualize_with:
                origin_candidates = [
                    a for a in chatbot_expert_apps_role_priority_app
                    if a.get("app_id") == app_to_mutualize_with or
                    str(a.get("app_id")) == str(app_to_mutualize_with)
                ]
                if origin_candidates:
                    origin_app = origin_candidates[0]
                    mutualized_app = app
                    break
        
        if not origin_app or not mutualized_app:
            pytest.skip(
                "No pair of apps found with mutualize_with configured for chatbot_expert."
            )
        
        # STEP 1 : Créer un chat avec l'app d'origine
        get_chat_id_response = api_client.get(
            endpoint="/get_chat_id",
            app=origin_app
        )
        assert get_chat_id_response.status_code == 200
        new_chat_id = get_chat_id_response.text.strip()
        
        # Envoyer un message via chatbot_expert
        message_data = {
            "chat_id": new_chat_id,
            "user_question": "Quel disjoncteur pour une installation 32A - test load_previous"
        }
        
        send_response = api_client.post(
            endpoint="/get_chatbot_expert_answer",
            app=origin_app,
            data=message_data,
            stream=True
        )
        assert send_response.status_code == 200
        
        # Consommer le stream
        for _ in send_response.iter_lines():
            pass
        
        # STEP 2 : Charger le chat avec l'app mutualisée
        load_response = api_client.post(
            endpoint="/load_previous_chat",
            app=mutualized_app,
            data={"chat_id": new_chat_id}
        )
        
        assert load_response.status_code == 200, (
            f"Failed to load chat from mutualized app: {load_response.status_code}. "
            f"Response: {load_response.text}"
        )
        
        # Vérifier le contenu
        chat_data = load_response.json()
        assert chat_data.get("id") == new_chat_id, "Chat ID mismatch"
        assert "message_objects_list" in chat_data, "message_objects_list missing"
        
        print(f"\n✅ Load Previous Chat from Mutualized App Test PASSED")
        print(f"  Chat ID: {new_chat_id}")
        print(f"  Messages count: {len(chat_data.get('message_objects_list', []))}")
