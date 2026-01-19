"""
Tests métier pour l'endpoint /get_recent_chats.

Ce test valide le scénario de récupération de l'historique des chats :
- Authentification OAuth2
- Récupération de la liste des chats récents
- Validation de la structure de la réponse
"""
import pytest
from typing import Dict, Any
from marshmallow import ValidationError


class TestGetRecentChatsEndpoint:
    """Tests du scénario métier pour récupérer les chats récents."""
    
    def test_get_recent_chats_returns_list(
        self,
        api_client,
        common_app_authorized: Dict[str, Any],
        chat_item_schema
    ):
        """
        Test de récupération de la liste des chats récents.
        
        Ce test valide :
        1. L'authentification OAuth2 avec l'application
        2. L'appel à l'endpoint sans paramètres
        3. Le code de réponse HTTP 200
        4. La structure de la réponse (liste de chats)
        5. La structure de chaque élément de chat (chat_id, chat_title)
        
        Scénario métier :
        - Un utilisateur demande la liste de ses chats récents
        - Le système retourne une liste ordonnée de chats (max 50)
        - Chaque chat contient son ID et son titre
        
        Ce test est agnostique et peut fonctionner avec n'importe quelle
        implémentation d'API qui respecte le schéma défini.
        
        Expected : 200 OK avec une liste de chats (peut être vide)
        """
        # ============================================
        # GIVEN : Application avec fetch_history activé
        # ============================================
        endpoint = "/get_recent_chats"
        
        # ============================================
        # WHEN : Appel à l'endpoint
        # ============================================
        response = api_client.get(
            endpoint=endpoint,
            app=common_app_authorized
        )
        
        # ============================================
        # THEN : Validation de la réponse
        # ============================================
        
        # 1. Vérifier le code HTTP
        assert response.status_code == 200, (
            f"Expected HTTP 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # 2. Parser le JSON
        try:
            response_data = response.json()
        except Exception as e:
            pytest.fail(f"Failed to parse JSON response: {e}. Response: {response.text}")
        
        # 3. Vérifier que c'est une liste
        assert isinstance(response_data, list), (
            f"Expected response to be a list, got {type(response_data)}"
        )
        
        # 4. Valider la structure de chaque élément (si la liste n'est pas vide)
        if len(response_data) > 0:
            for i, chat in enumerate(response_data):
                try:
                    validated_chat = chat_item_schema.load(chat)
                except ValidationError as e:
                    pytest.fail(
                        f"Chat at index {i} validation failed: {e.messages}\n"
                        f"Chat data: {chat}"
                    )
                
                # Vérifier les champs obligatoires
                assert "chat_id" in validated_chat, f"Chat {i}: missing chat_id"
                assert "chat_title" in validated_chat, f"Chat {i}: missing chat_title"
                
                # Vérifier les types
                assert isinstance(validated_chat["chat_id"], str), (
                    f"Chat {i}: chat_id should be a string"
                )
                assert isinstance(validated_chat["chat_title"], str), (
                    f"Chat {i}: chat_title should be a string"
                )
                
                # Vérifier que les valeurs ne sont pas vides
                assert len(validated_chat["chat_id"]) > 0, (
                    f"Chat {i}: chat_id should not be empty"
                )
                assert len(validated_chat["chat_title"]) > 0, (
                    f"Chat {i}: chat_title should not be empty"
                )
        
        # 5. Vérifier que la liste ne dépasse pas 50 éléments (limite commune)
        assert len(response_data) <= 50, (
            f"Expected at most 50 chats, got {len(response_data)}"
        )
        
        # 6. Log des informations pour debug
        print(f"\n{'='*60}")
        print(f"✅ Get Recent Chats Test PASSED")
        print(f"{'='*60}")
        print(f"App ID: {common_app_authorized['app_id']}")
        print(f"Number of chats: {len(response_data)}")
        
        if len(response_data) > 0:
            print(f"\nFirst 5 chats:")
            for i, chat in enumerate(response_data[:5], 1):
                title_preview = chat.get('chat_title', '')[:50]
                print(f"  {i}. [{chat.get('chat_id', 'N/A')}] {title_preview}...")
        else:
            print("\n⚠️  No chats found (empty list returned)")
        
        print(f"{'='*60}\n")
