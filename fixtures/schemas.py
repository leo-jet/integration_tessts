"""
Schémas de validation Marshmallow pour les réponses API.

Ces schémas sont agnostiques et peuvent être utilisés pour valider
n'importe quelle implémentation d'API conforme.
"""
from marshmallow import Schema, fields, validate, ValidationError


class TopicSchema(Schema):
    """Schéma pour un topic dans le rapport de visite."""
    topic = fields.Str(required=True)
    topic_details = fields.Str(required=True)
    next_actions = fields.List(fields.Str(), required=False, allow_none=True)
    due_date = fields.Str(required=False, allow_none=True)
    innovative = fields.Bool(required=False, allow_none=True)


class VisitReportSchema(Schema):
    """Schéma pour le rapport de visite."""
    summary = fields.Str(required=True)
    topics = fields.List(fields.Nested(TopicSchema), required=True)


class CrmVisitReportResponseSchema(Schema):
    """Schéma de validation pour la réponse de /crm-visit-report."""
    visit_report = fields.Nested(VisitReportSchema, required=True)


class ErrorResponseSchema(Schema):
    """Schéma pour les réponses d'erreur."""
    errors = fields.Str(required=False)
    error = fields.Str(required=False)
    message = fields.Str(required=False)
    success = fields.Bool(required=False)


# ============================================================================
# Schémas pour les endpoints Common (fetch_history)
# ============================================================================

class ChatItemSchema(Schema):
    """Schéma pour un élément de chat dans la liste."""
    chat_id = fields.Str(required=True)
    chat_title = fields.Str(required=True)


class MessageObjectSchema(Schema):
    """Schéma pour un message dans l'historique."""
    role = fields.Str(required=True)
    text_content = fields.Str(required=True)


class LoadPreviousChatResponseSchema(Schema):
    """Schéma de validation pour la réponse de /load_previous_chat."""
    id = fields.Str(required=True)
    mode = fields.Str(required=False, allow_none=True)
    mode_id = fields.Str(required=False, allow_none=True)
    mode_version = fields.Str(required=False, allow_none=True)
    kb = fields.Str(required=False, allow_none=True)
    message_objects_list = fields.List(fields.Nested(MessageObjectSchema), required=True)


# Langues supportées
SUPPORTED_LANGUAGES = [
    "en", "nl", "fi", "fr", "de", "ga", "it", "sv", "ca", "hr", "cs", "da",
    "et", "is", "lv", "lt", "lb", "no", "pl", "pt", "ro", "ru", "sr", "sk",
    "sl", "es", "zh", "hi", "ar", "bn", "ja", "pa"
]


# Segments clients supportés
SUPPORTED_SEGMENTS = ["IND", "TER", "RES"]


def validate_language(lang: str) -> None:
    """Valide qu'une langue est supportée."""
    if lang not in SUPPORTED_LANGUAGES:
        raise ValidationError(f"Language '{lang}' not supported. Must be one of: {', '.join(SUPPORTED_LANGUAGES)}")


def validate_segment(segment: str) -> None:
    """Valide qu'un segment est supporté."""
    if segment not in SUPPORTED_SEGMENTS:
        raise ValidationError(f"Segment '{segment}' not supported. Must be one of: {', '.join(SUPPORTED_SEGMENTS)}")


# ============================================================================
# Schémas pour extract_from_kb
# ============================================================================

class KBResultMetadataSchema(Schema):
    """Schéma pour les métadonnées d'un résultat KB."""
    source = fields.Str(required=False)
    document_id = fields.Str(required=False)
    chunk_id = fields.Str(required=False)
    title = fields.Str(required=False)
    page = fields.Int(required=False)
    
    class Meta:
        unknown = "INCLUDE"


class KBResultSchema(Schema):
    """Schéma pour un résultat d'extraction de la knowledge base."""
    content = fields.Str(required=True)
    score = fields.Float(required=True)
    metadata = fields.Nested(KBResultMetadataSchema, required=False)
    
    @validate.validates("score")
    def validate_score(self, value):
        """Valide que le score est entre 0 et 1."""
        if not 0 <= value <= 1:
            raise ValidationError("Score must be between 0 and 1")


class KBExtractResponseSchema(Schema):
    """Schéma pour la réponse de extract_from_kb."""
    results = fields.List(fields.Nested(KBResultSchema), required=True)
    query = fields.Str(required=False)
    total_results = fields.Int(required=False)
    processing_time_ms = fields.Float(required=False)
