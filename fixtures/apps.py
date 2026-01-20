"""
Gestion des applications pour les tests d'intégration.

Système générique de chargement et validation des applications
depuis un fichier JSON avec support pour le filtrage multi-critères.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from marshmallow import Schema, fields, ValidationError, validates_schema


class OAuthConfigSchema(Schema):
    """Schéma de validation pour oauth_config."""
    client_id_env_var = fields.Str(required=True)
    client_secret_env_var = fields.Str(required=False)  # Optionnel pour MSAL user flow
    tenant_id = fields.Str(required=True)
    scope = fields.Str(required=True)
    
    # Champs spécifiques pour MSAL (role_priority="user")
    authority = fields.Str(required=False)  # Ex: "https://login.microsoftonline.com/tenant_id"
    apim_scope_env_var = fields.Str(required=False)  # Variable d'env contenant le scope APIM
    user_token_env_var = fields.Str(required=False)  # Variable contenant le token user pré-généré


class AppSchema(Schema):
    """Schéma de validation pour une application."""
    app_id = fields.Str(required=True)
    app_name = fields.Str(required=True)
    date = fields.Str(required=False)
    role_priority = fields.Str(required=True)
    domain = fields.Str(allow_none=True, required=False)
    country = fields.Str(required=False)
    lang = fields.Str(required=False)
    webshop = fields.Str(required=False)
    roles = fields.List(fields.Str(), required=True)
    roles_test = fields.Dict(keys=fields.Str(), values=fields.Dict(), required=False)
    ocp_apim_subscription_key = fields.Str(required=True)
    oauth_config = fields.Nested(OAuthConfigSchema, required=True)
    fetch_history = fields.Int(required=False)
    mutualize_with = fields.Int(required=False)
    
    @validates_schema
    def validate_role_priority(self, data, **kwargs):
        """Valide que role_priority a une valeur valide."""
        valid_priorities = ["user", "app"]
        if data["role_priority"] not in valid_priorities:
            raise ValidationError(
                f"role_priority must be one of {valid_priorities}",
                field_name="role_priority"
            )


class AppLoader:
    """Chargeur d'applications avec validation."""
    
    def __init__(self, apps_json_path: Optional[Path] = None):
        """
        Initialise le chargeur d'applications.
        
        Args:
            apps_json_path: Chemin vers le fichier apps.json
                           (par défaut: data/apps.json relatif au script)
        """
        if apps_json_path is None:
            apps_json_path = Path(__file__).parent.parent / "data" / "apps.json"
        
        self.apps_json_path = apps_json_path
        self._apps: Optional[List[Dict[str, Any]]] = None
    
    def load_apps(self) -> List[Dict[str, Any]]:
        """
        Charge et valide les applications depuis apps.json.
        
        Returns:
            Liste d'applications validées
            
        Raises:
            FileNotFoundError: Si apps.json n'existe pas
            ValidationError: Si les données sont invalides
        """
        if self._apps is not None:
            return self._apps
        
        if not self.apps_json_path.exists():
            raise FileNotFoundError(
                f"apps.json not found at {self.apps_json_path}. "
                "Please create it using the template in data/apps.json.example"
            )
        
        with open(self.apps_json_path, "r", encoding="utf-8") as f:
            apps_data = json.load(f)
        
        # Valider chaque app
        schema = AppSchema()
        validated_apps = []
        
        for i, app in enumerate(apps_data):
            try:
                validated_app = schema.load(app)
                validated_apps.append(validated_app)
            except ValidationError as e:
                raise ValidationError(
                    f"Validation error in app at index {i} ({app.get('app_name', 'unknown')}): {e.messages}"
                )
        
        self._apps = validated_apps
        return self._apps
    
    def filter_apps(
        self,
        role: Optional[str] = None,
        role_priority: Optional[str] = None,
        country: Optional[str] = None,
        custom_filter: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filtre les applications selon des critères.
        
        Args:
            role: Filtre par rôle (ex: "crm_visit_report")
            role_priority: Filtre par priorité de rôle ("user" ou "app")
            country: Filtre par pays
            custom_filter: Fonction de filtrage personnalisée
            
        Returns:
            Liste des applications filtrées
        """
        apps = self.load_apps()
        filtered = apps
        
        if role is not None:
            filtered = [app for app in filtered if role in app.get("roles", [])]
        
        if role_priority is not None:
            filtered = [app for app in filtered if app.get("role_priority") == role_priority]
        
        if country is not None:
            filtered = [app for app in filtered if app.get("country") == country]
        
        if custom_filter is not None:
            filtered = [app for app in filtered if custom_filter(app)]
        
        return filtered


# Instance globale
app_loader = AppLoader()
