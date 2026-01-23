"""
Tests de scénario métier pour l'endpoint extract_from_knowledge_base.

L'endpoint extract_from_knowledge_base extrait des informations depuis une KB
et retourne une réponse en streaming SSE (Server-Sent Events).

Endpoint: POST /extract_from_knowledge_base
Content-Type: multipart/form-data
Response: text/event-stream
"""
import pytest
import json


def test_extract_from_knowledge_base_streaming(
    api_client,
    kb_roles_with_tests,
    get_chat_id
):
    """
    Test du scénario complet d'extraction depuis la knowledge base avec streaming.
    
    Parcourt tous les rôles KB configurés avec roles_test et teste chacun.
    
    Scénario:
    1. Génération d'un chat_id via l'endpoint get_chat_id_route
    2. Authentification OAuth2 automatique
    3. Envoi d'une requête d'extraction à la KB (multipart/form-data)
    4. Réception d'une réponse en streaming SSE
    5. Validation de la structure des événements SSE
    6. Vérification du contenu extrait
    
    Validations:
    - Code HTTP 200
    - Content-Type: text/event-stream
    - Format SSE valide (data: {...})
    - Événements contenant role et content
    - Contenu non vide
    """
    # Parcourir tous les rôles KB avec config de test
    for app, role_name, test_config in kb_roles_with_tests:
        print(f"\n🧪 Testing KB role '{role_name}' for app '{app['app_name']}'")
        
        # Étape 1: Générer un chat_id dynamique
        chat_id = get_chat_id(app=app)
        
        # Créer la requête avec le chat_id généré et la question standard
        request_data = test_config.copy()
        request_data["chat_id"] = chat_id
        request_data["user_question"] = "Which KB is this?"
        
        # Étape 2: Appel API avec multipart/form-data
        response = api_client.post(
            endpoint="/extract_from_knowledge_base",
            app=app,
            data=request_data,
            stream=True
        )
    
        # Étape 2: Validation du code HTTP
        assert response.status_code == 200, (
            f"[{role_name}] Expected HTTP 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # Étape 3: Validation du Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "text/event-stream" in content_type, (
            f"[{role_name}] Expected text/event-stream, got {content_type}"
        )
        
        # Étape 4: Parser les événements SSE
        sse_events = []
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                data_str = line[6:]  # Enlever "data: "
                try:
                    event_data = json.loads(data_str)
                    sse_events.append(event_data)
                except json.JSONDecodeError:
                    # Peut arriver si c'est juste du texte
                    sse_events.append({"raw": data_str})
        
        # Étape 5: Validation métier - Au moins un événement reçu
        assert len(sse_events) > 0, (
            f"[{role_name}] No SSE events received from streaming response"
        )
        
        # Étape 6: Validation métier - Structure des événements
        for idx, event in enumerate(sse_events):
            if "raw" not in event:
                # Événements structurés doivent avoir role/content OU event_type/answer
                has_standard_fields = "role" in event or "content" in event
                has_chatbot_fields = "event_type" in event or "answer" in event
                assert has_standard_fields or has_chatbot_fields, (
                    f"[{role_name}] Event {idx}: missing expected fields. Event: {event}"
                )
                
                # Valider le contenu selon le format
                content = event.get("content") or event.get("answer")
                if content is not None:
                    assert isinstance(content, str), (
                        f"[{role_name}] Event {idx}: content/answer is not a string"
                    )
        
        # Étape 7: Validation métier - Extraire le contenu complet
        full_content = ""
        for event in sse_events:
            # Support both formats: 'content' (standard) and 'answer' (chatbot_answer)
            content = event.get("content") or event.get("answer") or ""
            full_content += content
        
        assert len(full_content) > 0, (
            f"[{role_name}] No content extracted from knowledge base"
        )
        
        # Étape 8: Validation métier - Le contenu doit contenir le nom du rôle (key de roles_test)
        full_content_lower = full_content.lower()
        role_name_lower = role_name.lower()
        
        assert role_name_lower in full_content_lower, (
            f"[{role_name}] Expected role name '{role_name}' to be found in KB response. "
            f"Content preview: {full_content[:200]}..."
        )
        
        print(f"   ✅ Role '{role_name}' test passed:")
        print(f"      - App: {app['app_name']}")
        print(f"      - Chat ID: {chat_id}")
        print(f"      - KB ID: {test_config.get('kb_id', 'N/A')}")
        print(f"      - Question: Which KB is this?")
        print(f"      - SSE events received: {len(sse_events)}")
        print(f"      - Total content length: {len(full_content)} chars")
        print(f"      - Role name '{role_name}' found in response: ✅")
        print(f"      - Content preview: {full_content[:100]}...")


def test_extract_from_knowledge_base_missing_params(
    api_client,
    kb_app
):
    """
    Test avec paramètres manquants.
    
    Validations:
    - Code HTTP 400 (Bad Request)
    - Message d'erreur présent
    """
    # Requête sans user_question (requis)
    invalid_request = {
        "chat_id": "test_chat_123",
        "kb_id": "en - Documentation"
        # user_question manquant
    }
    
    response = api_client.post(
        endpoint="/extract_from_knowledge_base",
        app=kb_app,
        data=invalid_request
    )
    
    assert response.status_code == 400, (
        f"Expected HTTP 400 for missing params, got {response.status_code}"
    )
    
    # Vérifier qu'une erreur est retournée
    try:
        json_response = response.json()
        assert "errors" in json_response or "error" in json_response, (
            "Expected error message in response"
        )
    except Exception:
        # Peut être du texte brut
        assert len(response.text) > 0, "Expected error message"
    
    print(f"\n✅ Missing params test passed: HTTP 400 returned")


def test_extract_from_knowledge_base_all_configured_kbs(
    api_client,
    kb_roles_with_tests,
    get_chat_id
):
    """
    Test avec toutes les KBs configurées dans roles_test.
    
    Validations:
    - Toutes les KBs configurées sont testées
    - Chaque KB retourne une réponse valide (200 ou 403/400)
    """
    tested_count = 0
    
    for app, role_name, test_config in kb_roles_with_tests:
        kb_id = test_config.get("kb_id")
        
        if not kb_id:
            print(f"⚠️  Skipping {role_name}: no kb_id in roles_test")
            continue
        
        # Générer un chat_id dynamique pour chaque test
        chat_id = get_chat_id(app=app)
        request_data = test_config.copy()
        request_data["chat_id"] = chat_id
        request_data["user_question"] = "Which KB is this?"
        
        response = api_client.post(
            endpoint="/extract_from_knowledge_base",
            app=app,
            data=request_data,
            stream=True
        )
        
        # Accepter 200 (succès) ou 403 (KB non accessible) ou 400 (params invalides)
        assert response.status_code in [200, 403, 400], (
            f"Unexpected status {response.status_code} for "
            f"role={role_name}, kb_id={kb_id}, app={app['app_name']}"
        )
        
        if response.status_code == 200:
            # Vérifier que c'est du streaming
            content_type = response.headers.get("Content-Type", "")
            assert "text/event-stream" in content_type or "application/json" in content_type
        
        tested_count += 1
        print(f"   ✅ {role_name} ({kb_id}): HTTP {response.status_code}")
    
    print(f"\n✅ All configured KBs tested: {tested_count} KB(s)")

