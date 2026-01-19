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
