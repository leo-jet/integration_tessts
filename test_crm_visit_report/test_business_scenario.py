"""
Tests métier pour l'endpoint /crm-visit-report.

Ce test valide le scénario nominal complet :
- Authentification OAuth2
- Validation des paramètres d'entrée
- Structure de la réponse JSON
- Contenu métier du rapport de visite

Le test est agnostique et peut fonctionner avec n'importe quelle
implémentation de l'API CRM visit report.
"""
import pytest
from typing import Dict, Any
from marshmallow import ValidationError


class TestCrmVisitReportBusinessScenario:
    """Tests du scénario métier complet pour CRM Visit Report."""
    
    def test_crm_visit_report_complete_business_scenario(
        self,
        api_client,
        crm_app_authorized: Dict[str, Any],
        valid_crm_data: Dict[str, str],
        crm_response_schema
    ):
        """
        Test du scénario métier complet pour le formatage d'un rapport de visite.
        
        Ce test valide :
        1. L'authentification OAuth2 avec l'application
        2. L'appel à l'endpoint avec des données valides
        3. Le code de réponse HTTP 200
        4. La structure complète de la réponse JSON (via Marshmallow)
        5. Le contenu métier (summary, topics, next_actions, etc.)
        
        Scénario métier :
        - Un utilisateur saisit des notes de visite non structurées
        - Le système transforme ces notes en JSON structuré
        - La réponse contient un résumé et des sujets détaillés avec actions
        
        Ce test est agnostique et peut fonctionner avec n'importe quelle
        implémentation de l'API qui respecte le schéma défini.
        
        Expected : 200 OK avec un visit_report structuré valide
        """
        # ============================================
        # GIVEN : Données de visite non structurées
        # ============================================
        endpoint = "/crm-visit-report"
        
        # ============================================
        # WHEN : Appel à l'endpoint
        # ============================================
        response = api_client.post(
            endpoint=endpoint,
            app=crm_app_authorized,
            data=valid_crm_data
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
        
        # 3. Valider la structure avec Marshmallow
        try:
            validated_data = crm_response_schema.load(response_data)
        except ValidationError as e:
            pytest.fail(
                f"Response schema validation failed: {e.messages}\n"
                f"Response data: {response_data}"
            )
        
        # 4. Vérifier la présence du visit_report
        assert "visit_report" in validated_data, "visit_report key missing in response"
        visit_report = validated_data["visit_report"]
        
        # 5. Vérifier la structure du visit_report
        assert "summary" in visit_report, "summary key missing in visit_report"
        assert "topics" in visit_report, "topics key missing in visit_report"
        
        # 6. Vérifier le summary
        summary = visit_report["summary"]
        assert isinstance(summary, str), f"summary should be a string, got {type(summary)}"
        assert len(summary) > 0, "summary should not be empty"
        
        # 7. Vérifier les topics
        topics = visit_report["topics"]
        assert isinstance(topics, list), f"topics should be a list, got {type(topics)}"
        assert len(topics) > 0, "topics list should not be empty"
        
        # 8. Vérifier la structure de chaque topic
        for i, topic in enumerate(topics):
            assert "topic" in topic, f"Topic {i}: 'topic' field missing"
            assert "topic_details" in topic, f"Topic {i}: 'topic_details' field missing"
            
            # Vérifier les types
            assert isinstance(topic["topic"], str), f"Topic {i}: 'topic' should be a string"
            assert isinstance(topic["topic_details"], str), f"Topic {i}: 'topic_details' should be a string"
            
            # Vérifier que les champs ne sont pas vides
            assert len(topic["topic"]) > 0, f"Topic {i}: 'topic' should not be empty"
            assert len(topic["topic_details"]) > 0, f"Topic {i}: 'topic_details' should not be empty"
            
            # Vérifier les champs optionnels s'ils existent
            if "next_actions" in topic:
                assert isinstance(topic["next_actions"], (list, type(None))), (
                    f"Topic {i}: 'next_actions' should be a list or None"
                )
                if topic["next_actions"]:
                    for action in topic["next_actions"]:
                        assert isinstance(action, str), (
                            f"Topic {i}: each action in 'next_actions' should be a string"
                        )
            
            if "due_date" in topic:
                assert isinstance(topic["due_date"], (str, type(None))), (
                    f"Topic {i}: 'due_date' should be a string or None"
                )
            
            if "innovative" in topic:
                assert isinstance(topic["innovative"], (bool, type(None))), (
                    f"Topic {i}: 'innovative' should be a boolean or None"
                )
        
        # 9. Vérifications métier avancées
        # Vérifier que le summary correspond à la langue demandée
        target_lang = valid_crm_data["target_lang"]
        if target_lang in ["en", "fr", "de", "es"]:
            # Vérifier que le summary n'est pas vide et contient du texte significatif
            words = summary.split()
            assert len(words) >= 5, f"Summary should contain at least 5 words, got {len(words)}"
            # Vérifier qu'il y a des mots d'au moins 3 caractères
            meaningful_words = [w for w in words if len(w) >= 3]
            assert len(meaningful_words) >= 3, "Summary should contain meaningful words"
        
        # 10. Log des informations pour debug
        print(f"\n{'='*60}")
        print(f"✅ CRM Visit Report Test PASSED")
        print(f"{'='*60}")
        print(f"App ID: {crm_app_authorized['app_id']}")
        print(f"Target language: {target_lang}")
        print(f"Summary length: {len(summary)} characters")
        print(f"Number of topics: {len(topics)}")
        print(f"\nSummary preview:")
        preview_length = min(200, len(summary))
        print(f"  {summary[:preview_length]}{'...' if len(summary) > preview_length else ''}")
        print(f"\nTopics:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic['topic']}")
            if "next_actions" in topic and topic["next_actions"]:
                actions_preview = topic["next_actions"][:2]
                print(f"     Actions: {', '.join(actions_preview)}{'...' if len(topic['next_actions']) > 2 else ''}")
        print(f"{'='*60}\n")
