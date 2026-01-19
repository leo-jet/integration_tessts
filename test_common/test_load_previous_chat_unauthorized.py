"""
Tests négatifs pour l'endpoint /load_previous_chat.

Ces tests valident que l'accès est correctement restreint
aux applications avec fetch_history activé.
"""
import pytest
from typing import Dict, Any


class TestLoadPreviousChatUnauthorized:
    """Tests d'accès non autorisé pour load_previous_chat."""
    
    def test_load_previous_chat_without_fetch_history_denied(
        self,
        api_client,
        common_app_unauthorized: Dict[str, Any],
        test_chat_id: str
    ):
        """
        Test que les apps sans fetch_history ne peuvent pas accéder à load_previous_chat.
        
        Ce test valide :
        1. L'authentification OAuth2 fonctionne
        2. L'app sans fetch_history=1 est rejetée
        3. Le code de réponse est 401 ou 403
        
        Scénario de sécurité :
        - Une application sans droits fetch_history tente de charger un chat
        - Le système refuse l'accès avec une erreur d'autorisation
        
        Expected : 401 Unauthorized ou 403 Forbidden
        """
        # ============================================
        # GIVEN : Application SANS fetch_history
        # ============================================
        endpoint = "/load_previous_chat"
        
        assert common_app_unauthorized.get("fetch_history", 0) == 0, (
            "Test app should NOT have fetch_history enabled"
        )
        
        data = {
            "chat_id": test_chat_id
        }
        
        # ============================================
        # WHEN : Tentative d'accès à l'endpoint
        # ============================================
        response = api_client.post(
            endpoint=endpoint,
            app=common_app_unauthorized,
            data=data
        )
        
        # ============================================
        # THEN : Validation du refus d'accès
        # ============================================
        
        # 1. Vérifier le code HTTP (401 ou 403)
        assert response.status_code in [401, 403], (
            f"Expected HTTP 401 or 403 (Unauthorized/Forbidden), got {response.status_code}. "
            f"An app without fetch_history should not be able to load previous chats. "
            f"Response: {response.text}"
        )
        
        # 2. Log des informations pour debug
        print(f"\n{'='*60}")
        print(f"✅ Load Previous Chat Unauthorized Test PASSED")
        print(f"{'='*60}")
        print(f"App ID: {common_app_unauthorized['app_id']}")
        print(f"fetch_history: {common_app_unauthorized.get('fetch_history', 0)}")
        print(f"Chat ID attempted: {test_chat_id}")
        print(f"HTTP Status: {response.status_code} (Access correctly denied)")
        print(f"{'='*60}\n")
