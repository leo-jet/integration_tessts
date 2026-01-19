"""
Tests de mutualisation des chats entre applications (mutualize_with).

Ces tests valident que les chats créés par une application peuvent
être visibles par une autre application qui a mutualize_with configuré.
"""
import pytest
from typing import Dict, Any, List


class TestGetRecentChatsMutualizeWith:
    """Tests de mutualisation des chats entre apps."""
    
    def test_mutualized_app_can_see_chats_from_origin_app(
        self,
        api_client,
        common_apps_with_fetch_history: List[Dict[str, Any]]
    ):
        """
        Test qu'une app mutualisée peut voir les chats d'une autre app.
        
        Ce test valide :
        1. Création d'un chat avec l'app d'origine (app A)
        2. Récupération des chats avec l'app mutualisée (app B avec mutualize_with=A)
        3. Vérification que le chat créé par A est visible par B
        
        Scénario métier :
        - Un utilisateur commence une conversation sur l'app A
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
        
        for app in common_apps_with_fetch_history:
            mutualize_with = app.get("mutualize_with")
            if mutualize_with and mutualize_with != 0:
                # Cette app est mutualisée, trouver l'app d'origine
                origin_candidates = [
                    a for a in common_apps_with_fetch_history
                    if a.get("app_id") == mutualize_with or
                    str(a.get("app_id")) == str(mutualize_with)
                ]
                if origin_candidates:
                    origin_app = origin_candidates[0]
                    mutualized_app = app
                    break
        
        if not origin_app or not mutualized_app:
            pytest.skip(
                "No pair of apps found with mutualize_with configured. "
                "Add two apps in apps.json where one has mutualize_with pointing to the other's app_id."
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
        print(f"📝 Creating test chat with origin app")
        print(f"{'='*60}")
        print(f"Origin App ID: {origin_app['app_id']}")
        print(f"New Chat ID: {new_chat_id}")
        
        # 1.2. Envoyer un message pour créer le chat
        message_data = {
            "chat_id": new_chat_id,
            "user_question": "Test message for mutualize_with integration test",
            "model_name": "gpt4",
            "engine": "gpt-4o-mini",
            "reasoning_level": "low"
        }
        
        send_message_response = api_client.post(
            endpoint="/get_answer_stream",
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
        
        print(f"✅ Chat created successfully ({chunks_received} chunks received)")
        
        # ============================================
        # STEP 2 : Récupérer les chats avec l'app mutualisée
        # ============================================
        
        print(f"\n{'='*60}")
        print(f"🔍 Checking if mutualized app can see the chat")
        print(f"{'='*60}")
        print(f"Mutualized App ID: {mutualized_app['app_id']}")
        print(f"mutualize_with: {mutualized_app.get('mutualize_with')}")
        
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
            f"Chat {new_chat_id} created by origin app was NOT found in mutualized app's recent chats. "
            f"This indicates mutualize_with is not working correctly. "
            f"Found {len(chats)} chats in mutualized app."
        )
        
        print(f"\n{'='*60}")
        print(f"✅ Mutualize With Test PASSED")
        print(f"{'='*60}")
        print(f"Origin App: {origin_app['app_name']}")
        print(f"Mutualized App: {mutualized_app['app_name']}")
        print(f"Test Chat ID: {new_chat_id}")
        print(f"Status: Chat successfully shared between apps")
        print(f"{'='*60}\n")
