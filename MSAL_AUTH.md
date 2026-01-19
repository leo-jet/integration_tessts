# Authentification MSAL pour apps User

## 📋 Vue d'ensemble

Le framework supporte deux types d'authentification selon `role_priority` :

| role_priority | Type d'auth | Méthode | Cas d'usage |
|---------------|-------------|---------|-------------|
| `app` | OAuth2 Client Credentials | Automatique | Applications service-to-service |
| `user` | MSAL Token | Pré-généré ou Mock | Applications avec contexte utilisateur |

## 🔧 Configuration pour apps User

### 1. Structure dans apps.json

```json
{
  "app_id": "33333333-3333-3333-3333-333333333333",
  "app_name": "your-user-app",
  "role_priority": "user",
  "oauth_config": {
    "client_id_env_var": "USER_APP_CLIENT_ID",
    "tenant_id": "00000000-0000-0000-0000-000000000000",
    "authority": "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000",
    "scope": "api://00000000-0000-0000-0000-000000000000/.default",
    "apim_scope": "https://management.azure.com/.default",
    "user_token_env_var": "USER_APP_MSAL_TOKEN"
  }
}
```

### 2. Variables d'environnement (.env)

```bash
# Client ID pour l'app user
USER_APP_CLIENT_ID=your-client-id

# Token MSAL pré-généré
USER_APP_MSAL_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGc...

# OU mock token pour tests sans auth réelle
MOCK_USER_TOKEN=mock_token_for_testing
```

## 🚀 Générer un token MSAL

### Option 1 : Script automatique (Recommandé)

```bash
# Installer MSAL (optionnel)
pip install msal

# Générer le token
python tools/generate_msal_token.py
```

Le script va :
1. Lire la configuration depuis `.env`
2. Initier un device code flow
3. Afficher un code à saisir sur https://microsoft.com/devicelogin
4. Attendre l'authentification
5. Sauvegarder le token dans `.env`

### Option 2 : Manuellement avec MSAL

```python
from msal import PublicClientApplication

client_id = "your-client-id"
authority = "https://login.microsoftonline.com/your-tenant-id"
scopes = ["api://your-api-id/.default"]

app = PublicClientApplication(client_id=client_id, authority=authority)
flow = app.initiate_device_flow(scopes=scopes)

print(flow["message"])  # Instructions pour l'utilisateur

result = app.acquire_token_by_device_flow(flow)
token = result["access_token"]

print(f"Token: {token}")
```

### Option 3 : Mock token pour tests

Pour les tests sans authentification réelle :

```bash
# Dans .env
MOCK_USER_TOKEN=mock_token_for_testing_purposes
```

Le système utilisera automatiquement ce mock si aucun vrai token n'est disponible.

## 🧪 Utilisation dans les tests

Les tests utilisent automatiquement le bon type d'authentification selon `role_priority` :

```python
def test_with_user_app(api_client, user_app):
    # L'authentification MSAL est gérée automatiquement
    response = api_client.get(
        endpoint="/get_recent_chats",
        app=user_app  # role_priority="user"
    )
    
    assert response.status_code == 200
```

## 🔍 Flux d'authentification

### Pour role_priority="app"
```
1. Lire client_id et client_secret depuis .env
2. Appeler token endpoint OAuth2
3. Recevoir access_token
4. Utiliser dans les requêtes API
```

### Pour role_priority="user"
```
1. Vérifier si USER_APP_MSAL_TOKEN existe dans .env
2. Si oui, utiliser ce token
3. Sinon, vérifier MOCK_USER_TOKEN
4. Si aucun, lever une erreur avec instructions
5. Utiliser le token dans les requêtes API
```

## ⚙️ Fixtures pour apps User

Le framework inclut des fixtures pour filtrer les apps user :

```python
@pytest.fixture
def user_apps(filter_apps_by):
    """Retourne toutes les apps avec role_priority='user'"""
    return filter_apps_by(role_priority="user")

@pytest.fixture
def user_app(user_apps):
    """Retourne la première app user trouvée"""
    if not user_apps:
        pytest.skip("No user apps configured")
    return user_apps[0]
```

Utilisation dans un test :

```python
def test_user_specific_feature(api_client, user_app):
    # user_app a automatiquement role_priority="user"
    response = api_client.get("/user-endpoint", app=user_app)
    assert response.status_code == 200
```

## 🛡️ Sécurité

### ⚠️ Durée de vie des tokens

Les tokens MSAL ont une durée de vie limitée (généralement 1h). Si vos tests durent longtemps :

1. **Régénérer le token avant chaque session** :
   ```bash
   python tools/generate_msal_token.py
   pytest test_common/ -v
   ```

2. **Utiliser des mock tokens** pour les tests non critiques :
   ```bash
   MOCK_USER_TOKEN=mock pytest test_common/ -v
   ```

### 🔒 Ne jamais committer de tokens

Ajoutez à `.gitignore` :
```
.env
*.token
```

## 📝 Troubleshooting

### Erreur : "No user token available"

```
AuthenticationError: No user token available for app your-user-app
```

**Solutions** :
1. Générer un token MSAL : `python tools/generate_msal_token.py`
2. Utiliser un mock : `export MOCK_USER_TOKEN=mock`
3. Vérifier que `USER_APP_MSAL_TOKEN` est dans `.env`

### Erreur : "Token expired"

Le token MSAL a expiré. Régénérez-le :
```bash
python tools/generate_msal_token.py
```

### Erreur : "Invalid token"

Vérifiez que :
1. Le `client_id` est correct
2. Le `scope` correspond à votre API
3. Le token n'est pas tronqué dans `.env`

## 📊 Comparaison App vs User

| Critère | App (role_priority="app") | User (role_priority="user") |
|---------|---------------------------|------------------------------|
| **Auth** | OAuth2 Client Credentials | MSAL Token |
| **Secret requis** | ✅ Oui (client_secret) | ❌ Non |
| **Interactif** | ❌ Non | ✅ Oui (première fois) |
| **Durée token** | 1h (auto-refresh) | 1h (manuel refresh) |
| **Contexte** | Service | Utilisateur |
| **Cache** | ✅ Oui | ❌ Non (manuel) |
| **Mock possible** | ❌ Non | ✅ Oui |

## 🎯 Bonnes pratiques

1. **Utilisez `role_priority="app"` par défaut** pour les tests automatisés
2. **Utilisez `role_priority="user"` uniquement** pour tester des features spécifiques au contexte utilisateur
3. **Mock les tokens user** dans CI/CD pour éviter l'authentification interactive
4. **Régénérez les tokens** avant les sessions de test longues
5. **Documentez les scopes requis** pour chaque app user

## 📚 Ressources

- [MSAL Python Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Azure AD Authentication Flows](https://docs.microsoft.com/en-us/azure/active-directory/develop/authentication-flows-app-scenarios)
- [Device Code Flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code)
