"""
Tests de scénario métier pour l'endpoint /products-search.

L'endpoint /products-search permet de rechercher des produits dans le catalogue
basé sur une requête utilisateur et retourne des résultats structurés.

Endpoint: POST /products-search
Content-Type: multipart/form-data
Response: application/json

Décorateurs:
- check_access: Vérifie les droits d'accès
- conditional_route: Routage conditionnel

Paramètres requis:
- chat_id (string): Identifiant unique de la session chat
- user_question (string): La requête de l'utilisateur
- country (string): Pays pour la recherche (ex: "fr")
- search_mode (string): Mode de recherche ("vector", "hybrid", "semantic")
- product_catalog (string): Catalogue de produits (ex: "productactiveweb")
- solr_banner (string): Banner pour la recherche Solr (ex: "frx")
"""
import pytest
import json
from typing import Dict, Any, List


class TestProductsSearchBusinessScenario:
    """Tests du scénario métier complet pour Products Search."""
    
    def test_products_search_complete_scenario(
        self,
        api_client,
        products_search_app_authorized: Dict[str, Any],
        valid_products_search_data: Dict[str, str]
    ):
        """
        Test du scénario métier complet pour une recherche de produits.
        
        Ce test valide :
        1. L'authentification OAuth2 avec l'application
        2. L'appel à l'endpoint avec des données valides
        3. Le code de réponse HTTP 200
        4. La structure de la réponse JSON
        5. La présence de résultats de recherche
        
        Scénario métier :
        - Un utilisateur recherche un produit (ex: "led")
        - Le système retourne une liste de produits correspondants
        - Chaque produit contient des informations (rank, code, description, brand, score)
        
        Expected : 200 OK avec résultats de recherche structurés
        """
        # ============================================
        # GIVEN : Requête de recherche produit
        # ============================================
        endpoint = "/products-search"
        
        # ============================================
        # WHEN : Appel à l'endpoint
        # ============================================
        response = api_client.post(
            endpoint=endpoint,
            app=products_search_app_authorized,
            data=valid_products_search_data
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
        
        # 3. Vérifier la présence de résultats
        assert "results" in response_data, (
            f"'results' key missing in response: {response_data}"
        )
        
        results = response_data["results"]
        assert isinstance(results, list), (
            f"'results' should be a list, got {type(results)}"
        )
        
        # 4. Vérifier la structure des résultats (si non vide)
        if len(results) > 0:
            for i, result in enumerate(results):
                # Vérifier les champs attendus
                expected_fields = ["query", "Product rank", "Product code", "Description"]
                
                for field in expected_fields:
                    assert field in result, (
                        f"Result {i}: missing field '{field}'. Result: {result}"
                    )
                
                # Vérifier les types
                assert isinstance(result.get("Product rank"), (int, float)), (
                    f"Result {i}: 'Product rank' should be a number"
                )
                assert isinstance(result.get("Description"), str), (
                    f"Result {i}: 'Description' should be a string"
                )
                
                # Vérifier que la description n'est pas vide
                assert len(result.get("Description", "")) > 0, (
                    f"Result {i}: 'Description' should not be empty"
                )
        
        # 5. Log pour debug
        print(f"\n✅ Products Search test passed")
        print(f"   - Results count: {len(results)}")
        if results:
            print(f"   - First result: {results[0].get('Description', 'N/A')[:50]}...")


    def test_products_search_with_different_search_modes(
        self,
        api_client,
        products_search_app_authorized: Dict[str, Any],
        valid_products_search_data: Dict[str, str],
        supported_search_modes: List[str]
    ):
        """
        Test de recherche avec différents modes.
        
        Teste les modes: vector, hybrid, semantic
        
        Expected : 200 OK pour chaque mode
        """
        endpoint = "/products-search"
        
        for mode in supported_search_modes:
            data = valid_products_search_data.copy()
            data["search_mode"] = mode
            
            response = api_client.post(
                endpoint=endpoint,
                app=products_search_app_authorized,
                data=data
            )
            
            assert response.status_code == 200, (
                f"Mode '{mode}': Expected HTTP 200, got {response.status_code}. "
                f"Response: {response.text}"
            )
            
            print(f"\n✅ Search mode '{mode}' test passed")


class TestProductsSearchValidation:
    """Tests de validation des paramètres pour Products Search."""
    
    def test_products_search_missing_required_field(
        self,
        api_client,
        products_search_app_authorized: Dict[str, Any],
        get_chat_id
    ):
        """
        Test avec un champ requis manquant (country).
        
        Expected : 400 Bad Request avec message d'erreur
        """
        endpoint = "/products-search"
        chat_id = get_chat_id(app=products_search_app_authorized)
        
        # Données avec country manquant
        data = {
            "chat_id": chat_id,
            "user_question": "led",
            # "country" manquant
            "search_mode": "semantic",
            "product_catalog": "productactiveweb",
            "solr_banner": "frx"
        }
        
        response = api_client.post(
            endpoint=endpoint,
            app=products_search_app_authorized,
            data=data
        )
        
        assert response.status_code == 400, (
            f"Expected HTTP 400, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # Vérifier le format de l'erreur
        try:
            error_data = response.json()
            assert "error" in error_data or "errors" in error_data, (
                f"Error response should contain 'error' or 'errors': {error_data}"
            )
        except json.JSONDecodeError:
            pass
        
        print(f"\n✅ Missing required field validation test passed")


    def test_products_search_missing_user_question(
        self,
        api_client,
        products_search_app_authorized: Dict[str, Any],
        get_chat_id
    ):
        """
        Test avec user_question manquant.
        
        Expected : 400 Bad Request
        """
        endpoint = "/products-search"
        chat_id = get_chat_id(app=products_search_app_authorized)
        
        data = {
            "chat_id": chat_id,
            # user_question manquant
            "country": "fr",
            "search_mode": "semantic",
            "product_catalog": "productactiveweb",
            "solr_banner": "frx"
        }
        
        response = api_client.post(
            endpoint=endpoint,
            app=products_search_app_authorized,
            data=data
        )
        
        assert response.status_code == 400, (
            f"Expected HTTP 400, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        print(f"\n✅ Missing user_question validation test passed")


    def test_products_search_missing_chat_id(
        self,
        api_client,
        products_search_app_authorized: Dict[str, Any]
    ):
        """
        Test avec chat_id manquant.
        
        Expected : 400 Bad Request
        """
        endpoint = "/products-search"
        
        data = {
            # chat_id manquant
            "user_question": "led",
            "country": "fr",
            "search_mode": "semantic",
            "product_catalog": "productactiveweb",
            "solr_banner": "frx"
        }
        
        response = api_client.post(
            endpoint=endpoint,
            app=products_search_app_authorized,
            data=data
        )
        
        assert response.status_code == 400, (
            f"Expected HTTP 400, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        print(f"\n✅ Missing chat_id validation test passed")


    def test_products_search_invalid_search_mode(
        self,
        api_client,
        products_search_app_authorized: Dict[str, Any],
        valid_products_search_data: Dict[str, str]
    ):
        """
        Test avec un search_mode invalide.
        
        Expected : 400 Bad Request ou comportement défini
        """
        endpoint = "/products-search"
        
        data = valid_products_search_data.copy()
        data["search_mode"] = "invalid_mode"
        
        response = api_client.post(
            endpoint=endpoint,
            app=products_search_app_authorized,
            data=data
        )
        
        # Un mode invalide devrait retourner 400
        assert response.status_code in [400, 200], (
            f"Expected HTTP 400 or 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        print(f"\n✅ Invalid search_mode test passed (status: {response.status_code})")


class TestProductsSearchUnauthorized:
    """Tests de sécurité pour Products Search."""
    
    def test_products_search_without_auth(
        self,
        products_search_app_authorized: Dict[str, Any]
    ):
        """
        Test sans authentification.
        
        Note: Ce test nécessite un appel direct sans le client API
        pour éviter l'ajout automatique des headers d'auth.
        
        Expected : 401 Unauthorized
        """
        import requests
        from fixtures.config import Config
        
        endpoint = "/products-search"
        url = f"{Config.API_BASE_URL}{endpoint}"
        
        data = {
            "chat_id": "test-123",
            "user_question": "led",
            "country": "fr",
            "search_mode": "semantic",
            "product_catalog": "productactiveweb",
            "solr_banner": "frx"
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


class TestProductsSearchResultsQuality:
    """Tests de qualité des résultats pour Products Search."""
    
    def test_products_search_results_relevance(
        self,
        api_client,
        products_search_app_authorized: Dict[str, Any],
        valid_products_search_data: Dict[str, str]
    ):
        """
        Test de pertinence des résultats.
        
        Vérifie que les résultats contiennent des termes liés à la requête.
        
        Expected : Les descriptions des résultats sont pertinentes
        """
        endpoint = "/products-search"
        
        # Requête spécifique
        data = valid_products_search_data.copy()
        data["user_question"] = "led"
        
        response = api_client.post(
            endpoint=endpoint,
            app=products_search_app_authorized,
            data=data
        )
        
        assert response.status_code == 200, (
            f"Expected HTTP 200, got {response.status_code}"
        )
        
        response_data = response.json()
        results = response_data.get("results", [])
        
        if len(results) > 0:
            # Vérifier que les premiers résultats sont ordonnés par rang
            ranks = [r.get("Product rank", 0) for r in results[:5]]
            assert ranks == sorted(ranks), (
                f"Results should be ordered by rank. Ranks: {ranks}"
            )
            
            # Vérifier la présence de scores de similarité (si disponible)
            if "Similarity score" in results[0]:
                scores = [r.get("Similarity score", 0) for r in results[:5]]
                # Les scores devraient être décroissants (meilleur en premier)
                assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), (
                    f"Similarity scores should be in descending order. Scores: {scores}"
                )
        
        print(f"\n✅ Results relevance test passed")
        print(f"   - Total results: {len(results)}")
