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
├── test_extract_from_kb/         # Tests Knowledge Base
│   ├── conftest.py              # Fixtures spécifiques KB
│   └── test_business_scenario.py # Test extraction KB
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

### ✅ Knowledge Base - `/extract_from_knowledge_base`
   - ✅ Test d'extraction depuis la knowledge base avec streaming SSE
   - ✅ Validation du format Server-Sent Events
   - ✅ Vérification du contenu extrait
   - ✅ Test avec différents kb_id
   - ✅ Test avec paramètres manquants (400)

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

> ⚠️ Les fichiers `.env.*` sont ignorés par Git pour des raisons de sécurité.

### 3. Configurer les applications

```bash
# Copier le template
cp data/apps.json.example data/apps.json

# Éditer data/apps.json avec vos apps et clés OCP
```

### 4. Lancer les tests

#### Via ligne de commande

```bash
# Tous les tests
pytest -v

# Tests CRM
pytest test_crm_visit_report/ -v

# Tests Common (fetch_history)
pytest test_common/ -v

# Tests Knowledge Base
pytest test_extract_from_kb/ -v

# Avec logs détaillés
pytest test_crm_visit_report/ -v -s -o log_cli=true -o log_cli_level=INFO
```

#### Via VS Code (configurations de debug)

Le projet inclut des configurations de lancement VS Code dans `.vscode/launch.json` :

| Configuration | Test | Env |
|---------------|------|-----|
| `Python: Pytest get chat id` | test_get_chat_id.py | DEV |
| `Python: Pytest get answer stream` | test_get_answer_stream_all_scenarios.py | DEV |
| `Python: Pytest get recent chats` | test_get_recent_chats_scenarios.py | UAT |
| `Python: Pytest CRM` | test_crm_visit_report/test_business_scenarios.py | UAT |
| `Pytest extract from kb` | test_extract_from_kb/test_business_scenario.py | UAT |
| `Pytest get answer stream` | test_get_answer_stream/test_business_scenario.py | UAT |
| `Pytest get recent chat` | test_common/test_get_recent_chats.py | UAT |
| `Pytest get recent chat : unauthorized apps` | test_common/test_get_recent_chats_unauthorized.py | UAT |

Pour lancer un test en debug :
1. Ouvrir VS Code
2. Aller dans l'onglet **Run and Debug** (Ctrl+Shift+D)
3. Sélectionner la configuration souhaitée
4. Appuyer sur **F5**

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
- Chatbot Expert
- Products Search
- Autres endpoints spécifiques
