# Tests d'intégration - CRM Visit Report

## 📁 Structure mise en place

```
integration_tests/
├── fixtures/                           # Fixtures modulaires réutilisables
│   ├── __init__.py
│   ├── config.py                      # Configuration (base_url, timeout, .env)
│   ├── auth.py                        # OAuth2 avec retry et cache
│   ├── apps.py                        # Chargement et filtrage des apps
│   ├── api_client.py                  # Client HTTP avec auth
│   └── schemas.py                     # Validation Marshmallow
│
├── data/
│   └── apps.json.example              # Template de configuration des apps
│
├── test_crm_visit_report/             # Tests CRM
│   ├── conftest.py                    # Fixtures spécifiques CRM
│   └── test_business_scenario.py      # Test métier complet
│
├── conftest.py                        # Fixtures globales
├── requirements.txt                   # Dépendances (+ marshmallow)
├── .env.example                       # Template variables d'env
└── SETUP_CRM.md                       # Ce fichier
```

## 🚀 Installation - Étapes détaillées

### 1. Installer les dépendances

```bash
cd integration_tests
pip install -r requirements.txt
```

### 2. Créer le fichier .env

Copier `.env.example` vers `.env` et remplir les valeurs :

```bash
cp .env.example .env
```

Éditer `.env` avec vos vraies valeurs :

```bash
# API Configuration
API_BASE_URL=https://your-api-endpoint.com

# Azure OAuth2 Configuration
AZURE_TENANT_ID=12345678-90ab-cdef-1234-567890abcdef

# Application Credentials
APP_CLIENT_ID=12345678-90ab-cdef-1234-567890abcdef
APP_CLIENT_SECRET=your_actual_secret_value_here
```

### 3. Créer le fichier data/apps.json

Copier `data/apps.json.example` vers `data/apps.json` :

```bash
cp data/apps.json.example data/apps.json
```

Éditer `data/apps.json` avec vos vraies applications :

```json
[
  {
    "app_id": "00000000-0000-0000-0000-000000000000",
    "app_name": "your-application-name",
    "date": "2026-01-01",
    "role_priority": "app",
    "domain": null,
    "country": "us",
    "lang": "en",
    "webshop": "example.com",
    "roles": [
      "crm_visit_report",
      "crm_visit_report_tester"
    ],
    "ocp_apim_subscription_key": "YOUR_SUBSCRIPTION_KEY_HERE",
    "oauth_config": {
      "client_id_env_var": "APP_CLIENT_ID",
      "client_secret_env_var": "APP_CLIENT_SECRET",
      "scope": "api://00000000-0000-0000-0000-000000000000/.default"
    },
    "fetch_history": 0,
    "mutualize_with": 0
  }
]
```

**Important** : Remplacer `YOUR_SUBSCRIPTION_KEY_HERE` par votre vraie clé de souscription API.

## ✅ Vérification de la configuration

### Test 1 : Vérifier que pytest fonctionne

```bash
pytest --version
```

Devrait afficher : `pytest 7.4.0` ou supérieur

### Test 2 : Vérifier que les fixtures se chargent

```bash
pytest --collect-only test_crm_visit_report/
```

Devrait afficher :
```
<Module test_business_scenario.py>
  <Class TestCrmVisitReportBusinessScenario>
    <Function test_crm_visit_report_complete_business_scenario>
```

### Test 3 : Vérifier que apps.json est valide

```bash
python -c "from fixtures.apps import app_loader; print(f'✅ {len(app_loader.load_apps())} apps loaded')"
```

## 🧪 Exécuter les tests

### Test complet CRM

```bash
pytest test_crm_visit_report/ -v
```

### Test avec logs détaillés

```bash
pytest test_crm_visit_report/ -v -s
```

### Test avec affichage du temps d'exécution

```bash
pytest test_crm_visit_report/ -v --durations=10
```

## 📊 Résultat attendu

```
test_crm_visit_report/test_business_scenario.py::TestCrmVisitReportBusinessScenario::test_crm_visit_report_complete_business_scenario PASSED

============================================================
✅ CRM Visit Report Test PASSED
============================================================
App ID: 00000000-0000-0000-0000-000000000000
Target language: en
Summary length: 187 characters
Number of topics: 2

Summary preview:
  The customer expressed concerns regarding delivery times but was satisfied...

Topics:
  1. Delivery Issues
     Actions: Follow up on shipping, Contact logistics team
  2. Platform Satisfaction
     Actions: Gather feedback
============================================================

======================== 1 passed in 2.34s =========================
```

## 🔍 Ce qui est testé

Le test `test_crm_visit_report_complete_business_scenario` valide :

1. ✅ **Authentification OAuth2**
   - Récupération automatique du token
   - Gestion du cache et de l'expiration
   - Retry avec backoff exponentiel

2. ✅ **Appel API**
   - Headers corrects (Authorization + Ocp-Apim-Subscription-Key)
   - Données en multipart/form-data
   - Timeout configuré

3. ✅ **Validation HTTP**
   - Code 200 OK
   - Content-Type JSON

4. ✅ **Validation de structure** (Marshmallow)
   - Présence de `visit_report`
   - Présence de `summary` (string non vide)
   - Présence de `topics` (array non vide)
   - Structure de chaque topic :
     - `topic` (string, requis)
     - `topic_details` (string, requis)
     - `next_actions` (array de strings, optionnel)
     - `due_date` (string, optionnel)
     - `innovative` (boolean, optionnel)

5. ✅ **Validation métier**
   - Summary en français (si target_lang="fr")
   - Topics avec contenu non vide
   - Next actions bien formatées

## 🐛 Troubleshooting

### Erreur : "AZURE_TENANT_ID is required"

➡️ Vérifier que `.env` existe et contient `AZURE_TENANT_ID`

```bash
cat .env | grep AZURE_TENANT_ID
```

### Erreur : "apps.json not found"

➡️ Créer `data/apps.json` à partir de `data/apps.json.example`

```bash
cp data/apps.json.example data/apps.json
```

### Erreur : "No apps found with role='crm_visit_report'"

➡️ Vérifier que `data/apps.json` contient au moins une app avec :
- `"role_priority": "app"`
- `"crm_visit_report"` dans `"roles"`

### Erreur : "OAuth2 failed with status 401"

➡️ Vérifier les credentials dans `.env` :

```bash
# Tester manuellement l'authentification OAuth2
curl -X POST "https://login.microsoftonline.com/$AZURE_TENANT_ID/oauth2/v2.0/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=$APP_CLIENT_ID" \
  -d "client_secret=$APP_CLIENT_SECRET" \
  -d "scope=api://YOUR_SCOPE_ID/.default"
```

### Erreur : "HTTP 401 Unauthorized" sur l'endpoint

➡️ Vérifier la clé OCP dans `data/apps.json` :

```json
"ocp_apim_subscription_key": "YOUR_REAL_KEY_HERE"
```

### Erreur : "Schema validation failed"

➡️ L'API a retourné une structure différente. Vérifier avec :

```bash
pytest test_crm_visit_report/ -v -s --tb=short
```

## 📚 Prochaines étapes

Une fois le test CRM fonctionnel :

1. **Ajouter des tests négatifs** (400, 401, 403)
   - Paramètres manquants
   - Valeurs invalides
   - Apps non autorisées

2. **Migrer les autres endpoints** vers cette architecture
   - knowledge_base
   - chatbot_expert
   - products_search
   - common

3. **Intégrer dans CI/CD**
   - Pipeline pytest
   - Coverage report
   - Notifications

## 💡 Utilisation des fixtures

### Filtrer les apps par critères

```python
def test_something(filter_apps_by):
    # Toutes les apps CRM avec role_priority="app"
    crm_apps = filter_apps_by(role="crm_visit_report", role_priority="app")
    
    # Apps par pays
    be_apps = filter_apps_by(country="be")
    
    # Filtrage personnalisé
    def is_production(app):
        return "prod" in app["app_name"].lower()
    
    prod_apps = filter_apps_by(custom_filter=is_production)
```

### Utiliser l'API client

```python
def test_something(api_client, crm_app_authorized):
    # POST request
    response = api_client.post(
        endpoint="/crm-visit-report",
        app=crm_app_authorized,
        data={"key": "value"}
    )
    
    # GET request
    response = api_client.get(
        endpoint="/get_recent_chats",
        app=crm_app_authorized,
        params={"limit": 10}
    )
```

## 🎉 Succès !

Si tout fonctionne, vous avez maintenant :

✅ Architecture modulaire avec fixtures réutilisables  
✅ OAuth2 automatique avec retry et cache  
✅ Validation Marshmallow des réponses  
✅ Config externalisée (.env + apps.json)  
✅ Test métier complet pour CRM  
✅ Base pour migrer les autres endpoints  

**Prochaine étape** : Lancer le test !

```bash
pytest test_crm_visit_report/ -v -s
```
