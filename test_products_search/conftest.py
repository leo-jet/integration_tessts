"""
Fixtures spécifiques pour les tests Products Search.

L'endpoint /products-search permet de rechercher des produits
dans le catalogue basé sur une requête utilisateur.

Endpoint: POST /products-search
Content-Type: multipart/form-data
Response: application/json

Décorateurs:
- check_access: Vérifie les droits d'accès
- conditional_route: Routage conditionnel
"""
import pytest
from typing import List, Dict, Any


# Modes de recherche supportés
SUPPORTED_SEARCH_MODES = ["vector", "hybrid", "semantic"]

# Catalogues de produits supportés (exemples)
SUPPORTED_PRODUCT_CATALOGS = ["productactiveweb", "productactive", "productall"]

# Pays supportés (exemples basés sur les configurations Rexel)
SUPPORTED_COUNTRIES = ["fr", "de", "nl", "be", "uk", "es", "it", "pl", "cz", "sk", "at", "ch"]


@pytest.fixture(scope="module")
def products_search_apps_role_priority_app(filter_apps_by) -> List[Dict[str, Any]]:
    """
    Retourne les applications avec role_priority='app' autorisées pour Products Search.
    
    L'endpoint /products-search utilise le décorateur check_access,
    donc nécessite des apps avec le rôle approprié.
    
    Returns:
        Liste des apps avec le rôle products_search et role_priority='app'
    """
    apps = filter_apps_by(role="products_search", role_priority="app")
    
    if not apps:
        pytest.skip("No apps found with role='products_search' and role_priority='app'")
    
    return apps


@pytest.fixture
def products_search_app_authorized(products_search_apps_role_priority_app) -> Dict[str, Any]:
    """
    Retourne une application autorisée pour Products Search (première trouvée).
    
    Returns:
        Dict représentant une app autorisée
    """
    return products_search_apps_role_priority_app[0]


@pytest.fixture
def valid_products_search_data(get_chat_id, products_search_app_authorized) -> Dict[str, str]:
    """
    Données valides pour une requête Products Search.
    
    Returns:
        Dict avec tous les champs requis
    """
    chat_id = get_chat_id(app=products_search_app_authorized)
    return {
        "chat_id": chat_id,
        "user_question": "led",
        "country": "fr",
        "search_mode": "semantic",
        "product_catalog": "productactiveweb",
        "solr_banner": "frx"
    }


@pytest.fixture
def supported_search_modes() -> List[str]:
    """Liste des modes de recherche supportés."""
    return SUPPORTED_SEARCH_MODES


@pytest.fixture
def supported_countries() -> List[str]:
    """Liste des pays supportés."""
    return SUPPORTED_COUNTRIES


@pytest.fixture
def products_search_test_queries() -> List[Dict[str, str]]:
    """
    Liste de requêtes de test pour la recherche de produits.
    
    Returns:
        Liste de configurations de requêtes variées
    """
    return [
        {"query": "led", "description": "Simple keyword search"},
        {"query": "câble électrique 2.5mm", "description": "Technical specification"},
        {"query": "disjoncteur différentiel 30mA", "description": "Product category with specs"},
        {"query": "prise étanche IP65", "description": "Product with protection rating"},
        {"query": "schneider electric", "description": "Brand search"}
    ]
