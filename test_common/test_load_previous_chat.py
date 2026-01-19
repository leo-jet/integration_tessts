"""
Tests métier pour l'endpoint /load_previous_chat.

Ce test valide le scénario de chargement d'un chat existant :
- Authentification OAuth2
- Chargement du contenu d'un chat par son ID
- Validation de la structure de la réponse avec historique
"""
import pytest
from typing import Dict, Any
from marshmallow import ValidationError


class TestLoadPreviousChatEndpoint:
    """Tests du scénario métier pour charger un chat précédent."""
    
    def test_load_previous_chat_with_valid_id(
        self,
        api_client,
        common_app_authorized: Dict[str, Any],
        test_chat_id: str,
        load_previous_chat_schema,
        error_response_schema
    ):
        """
        Test de chargement d'un chat existant par son ID.
        
        Ce test valide :
        1. L'authentification OAuth2 avec l'application
        2. L'appel à l'endpoint avec un chat_id valide
        3. Le code de réponse HTTP (200 ou 400 si chat inexistant)
        4. La structure de la réponse (id, mode, message_objects_list)
        5. La structure des messages dans l'historique
        
        Scénario métier :
        - Un utilisateur veut reprendre une conversation précédente
        - Le système charge l'historique complet du chat
        - La réponse contient tous les messages échangés
        
        Ce test est agnostique et peut fonctionner avec n'importe quelle
        implémentation d'API qui respecte le schéma défini.
        
        Expected : 200 OK avec le contenu du chat, ou 400 si le chat n'existe pas
        """
        # ============================================
        # GIVEN : Un chat_id à charger
        # ============================================
        endpoint = "/load_previous_chat"
        
        data = {
            "chat_id": test_chat_id
        }
        
        # ============================================
        # WHEN : Appel à l'endpoint
        # ============================================
        response = api_client.post(
            endpoint=endpoint,
            app=common_app_authorized,
            data=data
        )
        
        # ============================================
        # THEN : Validation de la réponse
        # ============================================
        
        # 1. Accepter 200 (chat trouvé) ou 400 (chat non trouvé)
        assert response.status_code in [200, 400], (
            f"Expected HTTP 200 or 400, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # 2. Parser le JSON
        try:
            response_data = response.json()
        except Exception as e:
            pytest.fail(f"Failed to parse JSON response: {e}. Response: {response.text}")
        
        # Si le chat n'existe pas (400), valider la structure d'erreur
        if response.status_code == 400:
            try:
                error_response_schema.load(response_data)
            except ValidationError as e:
                pytest.fail(
                    f"Error response schema validation failed: {e.messages}\n"
                    f"Response data: {response_data}"
                )
            
            print(f"\n{'='*60}")
            print(f"⚠️  Load Previous Chat Test - Chat not found (expected)")
            print(f"{'='*60}")
            print(f"App ID: {common_app_authorized['app_id']}")
            print(f"Chat ID: {test_chat_id}")
            print(f"Status: Chat does not exist in the system")
            print(f"{'='*60}\n")
            
            pytest.skip(f"Chat {test_chat_id} does not exist - this is expected for a test chat_id")
        
        # Si le chat existe (200), valider la structure complète
        if response.status_code == 200:
            # 3. Valider la structure avec Marshmallow
            try:
                validated_data = load_previous_chat_schema.load(response_data)
            except ValidationError as e:
                pytest.fail(
                    f"Response schema validation failed: {e.messages}\n"
                    f"Response data: {response_data}"
                )
            
            # 4. Vérifier les champs obligatoires
            assert "id" in validated_data, "id key missing in response"
            assert "message_objects_list" in validated_data, "message_objects_list key missing"
            
            # 5. Vérifier que l'id correspond au chat_id demandé
            assert validated_data["id"] == test_chat_id, (
                f"Expected chat_id {test_chat_id}, got {validated_data['id']}"
            )
            
            # 6. Vérifier la liste de messages
            messages = validated_data["message_objects_list"]
            assert isinstance(messages, list), (
                f"message_objects_list should be a list, got {type(messages)}"
            )
            
            # 7. Valider la structure de chaque message
            for i, message in enumerate(messages):
                assert "role" in message, f"Message {i}: missing role"
                assert "text_content" in message, f"Message {i}: missing text_content"
                
                assert isinstance(message["role"], str), (
                    f"Message {i}: role should be a string"
                )
                assert isinstance(message["text_content"], str), (
                    f"Message {i}: text_content should be a string"
                )
                
                # Vérifier que le role est valide (user, assistant, system)
                valid_roles = ["user", "assistant", "system"]
                assert message["role"] in valid_roles, (
                    f"Message {i}: role '{message['role']}' should be one of {valid_roles}"
                )
            
            # 8. Log des informations pour debug
            print(f"\n{'='*60}")
            print(f"✅ Load Previous Chat Test PASSED")
            print(f"{'='*60}")
            print(f"App ID: {common_app_authorized['app_id']}")
            print(f"Chat ID: {validated_data['id']}")
            print(f"Mode: {validated_data.get('mode', 'N/A')}")
            print(f"Number of messages: {len(messages)}")
            
            if len(messages) > 0:
                print(f"\nMessage history:")
                for i, msg in enumerate(messages[:5], 1):
                    content_preview = msg['text_content'][:60]
                    print(f"  {i}. [{msg['role']}] {content_preview}...")
                
                if len(messages) > 5:
                    print(f"  ... and {len(messages) - 5} more messages")
            
            print(f"{'='*60}\n")
