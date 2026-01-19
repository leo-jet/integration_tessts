# Integration Tests

Tests d'intégration pour les endpoints de l'API avec architecture modulaire professionnelle.

## Structure

```
integration_tests/
├── fixtures/                      # Infrastructure modulaire réutilisable
│   ├── config.py                 # Configuration (base_url, timeout, .env)
│   ├── auth.py                   # OAuth2 avec retry et cache
│   ├── apps.py                   # Chargement et filtrage des apps
│   ├── api_client.py             # Client HTTP avec authentification
│   └── schemas.py                # Validation Marshmallow
│
├── data/
│   └── apps.json.example         # Template de configuration des apps
│
├── test_crm_visit_report/        # Tests CRM (architecture mature)
│   ├── conftest.py              # Fixtures spécifiques CRM
│   └── test_business_scenario.py # Test métier complet
│
├── test_common/                   # Tests Common (fetch_history)
│   ├── conftest.py              # Fixtures spécifiques Common
│   ├── test_get_recent_chats.py # Test récupération des chats
│   ├── test_get_recent_chats_unauthorized.py # Test accès refusé
│   ├── test_get_recent_chats_mutualize.py # Test mutualisation
│   ├── test_load_previous_chat.py # Test chargement d'un chat
│   └── test_load_previous_chat_unauthorized.py # Test accès refusé
│
├── conftest.py                   # Fixtures globales
├── requirements.txt              # Dépendances
├── .env.example                  # Template variables d'environnement
├── SETUP_CRM.md                  # Guide d'installation détaillé
└── REVIEW.md                     # Comparaison des architectures
```

## Endpoints testés

### ✅ CRM Visit Report - `/crm-visit-report` (Architecture mature)
   - ✅ Test métier complet avec OAuth2
   - ✅ Validation Marshmallow des réponses
   - ✅ Vérification de la structure JSON
   - ✅ Validation du contenu métier (summary, topics, actions)

### ✅ Common (fetch_history) - `/get_recent_chats` et `/load_previous_chat`
   - ✅ Test de récupération de la liste des chats récents
   - ✅ Test de chargement d'un chat avec historique
   - ✅ Tests d'accès non autorisé (apps sans fetch_history)
   - ✅ Test de mutualisation des chats (mutualize_with)
   - ✅ Validation Marshmallow des réponses
   - ✅ Vérification de la structure des messages

## 🚀 Quick Start

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer l'environnement

```bash
# Copier le template
cp .env.example .env

# Éditer .env avec vos vraies valeurs
# - AZURE_TENANT_ID
# - FRONTEND_CLIENT_ID
# - FRONTEND_CLIENT_SECRET
```

### 3. Configurer les applications

```bash
# Copier le template
cp data/apps.json.example data/apps.json

# Éditer data/apps.json avec vos apps et clés OCP
```

### 4. Lancer les tests
Tests Common (fetch_history)
pytest test_common/ -v

# Tous les tests
pytest -v

# Avec logs détaillés
pytest
# Tests CRM
pytest test_crm_visit_report/ -v

# Avec logs détaillés
pytest test_crm_visit_report/ -v -s
```

## 📚 Documentation détaillée

- [SETUP_CRM.md](SETUP_CRM.md) - Guide d'installation complet
- [MSAL_AUTH.md](MSAL_AUTH.md) - Authentification MSAL pour apps user
- [REVIEW.md](REVIEW.md) - Comparaison des architectures

## 🔧 Fixtures disponibles

### Fixtures globales (conftest.py)
- `config`: Configuration globale
- `base_url`: URL de base de l'API
- `apps`: Toutes les applications chargées depuis apps.json
- `filter_apps_by`: Factory pour filtrer les apps par critères
- `api_client`: Client HTTP avec authentification OAuth2
- `chat_id`: ID de chat par défaut

### Fixtures CRM (test_crm_visit_report/conftest.py)
- `crm_apps_role_priority_app`: Apps CRM avec role_priority='app'
- `crm_app_authorized`: Une app CRM autorisée
- `crm_response_schema`: Schéma de validation Marshmallow
- `valid_crm_data`: Données valides pour les requêtes

## 🎯 Caractéristiques

✅ **OAuth2 professionnel** - Retry, cache, backoff exponentiel  
✅ **Validation Marshmallow** - Structure de réponse garantie  
✅ **Factory fixtures** - Réutilisables et modulaires  
✅ **Config externalisée** - Pas de secrets en dur  
✅ **Tests métier complets** - Scénarios end-to-end  

## 📖 Pour aller plus loin

- [REVIEW.md](REVIEW.md) - Comparaison des architectures
- [SETUP_CRM.md](SETUP_CRM.md) - Guide d'installation détaillé

## 🔮 Prochaines étapes

Cette architecture modulaire est prête à être réutilisée pour migrer les autres endpoints :
- Knowledge Base
- Chatbot Expert
- Products Search
- Common endpoints
