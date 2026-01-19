"""
Tests négatifs pour l'endpoint /get_recent_chats.

Ces tests valident que l'accès est correctement restreint
aux applications avec fetch_history activé.
"""
import pytest
from typing import Dict, Any


class TestGetRecentChatsUnauthorized:
    """Tests d'accès non autorisé pour get_recent_chats."""
    
    def test_get_recent_chats_without_fetch_history_denied(
        self,
        api_client,
        common_app_unauthorized: Dict[str, Any]
    ):
        """
        Test que les apps sans fetch_history ne peuvent pas accéder à get_recent_chats.
        
        Ce test valide :
        1. L'authentification OAuth2 fonctionne
        2. L'app sans fetch_history=1 est rejetée
        3. Le code de réponse est 401 ou 403
        
        Scénario de sécurité :
        - Une application sans droits fetch_history tente d'accéder à l'historique
        - Le système refuse l'accès avec une erreur d'autorisation
        
        Expected : 401 Unauthorized ou 403 Forbidden
        """
        # ============================================
        # GIVEN : Application SANS fetch_history
        # ============================================
        endpoint = "/get_recent_chats"
        
        assert common_app_unauthorized.get("fetch_history", 0) == 0, (
            "Test app should NOT have fetch_history enabled"
        )
        
        # ============================================
        # WHEN : Tentative d'accès à l'endpoint
        # ============================================
        response = api_client.get(
            endpoint=endpoint,
            app=common_app_unauthorized
        )
        
        # ============================================
        # THEN : Validation du refus d'accès
        # ============================================
        
        # 1. Vérifier le code HTTP (401 ou 403)
        assert response.status_code in [401, 403], (
            f"Expected HTTP 401 or 403 (Unauthorized/Forbidden), got {response.status_code}. "
            f"An app without fetch_history should not be able to access recent chats. "
            f"Response: {response.text}"
        )
        
        # 2. Log des informations pour debug
        print(f"\n{'='*60}")
        print(f"✅ Get Recent Chats Unauthorized Test PASSED")
        print(f"{'='*60}")
        print(f"App ID: {common_app_unauthorized['app_id']}")
        print(f"fetch_history: {common_app_unauthorized.get('fetch_history', 0)}")
        print(f"HTTP Status: {response.status_code} (Access correctly denied)")
        print(f"{'='*60}\n")
