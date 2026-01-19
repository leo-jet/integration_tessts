"""
Script utilitaire pour générer un token MSAL pour les tests.

Ce script utilise MSAL pour obtenir un token interactif pour une application user.
Le token généré peut ensuite être utilisé dans les tests d'intégration.

Usage:
    python generate_msal_token.py
"""
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

try:
    from msal import PublicClientApplication
except ImportError:
    print("❌ MSAL not installed. Install it with: pip install msal")
    sys.exit(1)


def generate_msal_token(
    client_id: str,
    authority: str,
    scopes: list
) -> str:
    """
    Génère un token MSAL via device code flow.
    
    Args:
        client_id: Client ID de l'application
        authority: Authority URL (ex: https://login.microsoftonline.com/tenant_id)
        scopes: Liste des scopes requis
        
    Returns:
        str: Access token
    """
    app = PublicClientApplication(
        client_id=client_id,
        authority=authority
    )
    
    # Device code flow (interactif mais sans navigateur)
    flow = app.initiate_device_flow(scopes=scopes)
    
    if "user_code" not in flow:
        raise ValueError(
            "Failed to create device flow. "
            f"Error: {flow.get('error')}, {flow.get('error_description')}"
        )
    
    print("\n" + "="*60)
    print("🔐 MSAL Authentication - Device Code Flow")
    print("="*60)
    print(f"\n{flow['message']}\n")
    print("Waiting for authentication...")
    print("="*60 + "\n")
    
    # Attendre l'authentification
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        print("✅ Authentication successful!\n")
        return result["access_token"]
    else:
        error = result.get("error")
        error_desc = result.get("error_description")
        raise ValueError(f"Authentication failed: {error} - {error_desc}")


def main():
    """Point d'entrée principal."""
    
    print("\n" + "="*60)
    print("MSAL Token Generator for Integration Tests")
    print("="*60 + "\n")
    
    # Récupérer la configuration depuis .env
    client_id = os.getenv("USER_APP_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    apim_scope = os.getenv("APIM_SCOPE")
    
    if not client_id:
        print("❌ USER_APP_CLIENT_ID not found in .env file")
        sys.exit(1)
    
    if not tenant_id:
        print("❌ AZURE_TENANT_ID not found in .env file")
        sys.exit(1)
    
    if not apim_scope:
        print("❌ APIM_SCOPE not found in .env file")
        print("   Add: APIM_SCOPE=https://management.azure.com/.default")
        sys.exit(1)
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    
    # Utiliser le scope APIM depuis .env
    scopes = [apim_scope]
    
    print(f"\nConfiguration:")
    print(f"  Client ID: {client_id}")
    print(f"  Authority: {authority}")
    print(f"  Scopes: {scopes}")
    print()
    
    try:
        token = generate_msal_token(client_id, authority, scopes)
        
        print("\n" + "="*60)
        print("✅ Token Generated Successfully")
        print("="*60)
        print(f"\nAccess Token (first 50 chars):")
        print(f"  {token[:50]}...")
        print(f"\nFull token length: {len(token)} characters")
        
        print("\n" + "="*60)
        print("💾 Save this token to your .env file:")
        print("="*60)
        print(f"\nUSER_APP_MSAL_TOKEN={token}\n")
        
        # Proposer de sauvegarder automatiquement
        save = input("Save to .env automatically? (y/n): ").strip().lower()
        
        if save == 'y':
            with open('.env', 'a') as f:
                f.write(f"\n# Generated MSAL token on {os.popen('date').read().strip()}\n")
                f.write(f"USER_APP_MSAL_TOKEN={token}\n")
            print("✅ Token saved to .env file")
        else:
            print("⚠️  Remember to add the token to your .env file manually")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
