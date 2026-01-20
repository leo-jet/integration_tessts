"""
Tests de scénario métier pour l'endpoint get_answer_stream.

L'endpoint get_answer_stream permet d'obtenir une réponse streamée du chatbot
et retourne une réponse en streaming SSE (Server-Sent Events).

Endpoint: POST /get_answer_stream
Content-Type: multipart/form-data
Response: text/event-stream
"""
import pytest
import json


def test_get_answer_stream_basic(
    api_client,
    stream_roles_with_tests,
    get_chat_id
):
    """
    Test du scénario complet de streaming de réponse du chatbot.
    
    Parcourt tous les rôles configurés avec roles_test et teste chacun.
    
    Scénario:
    1. Génération d'un chat_id via l'endpoint get_chat_id
    2. Authentification OAuth2 automatique
    3. Envoi d'une question au chatbot (multipart/form-data)
    4. Réception d'une réponse en streaming SSE
    5. Validation de la structure des événements SSE
    6. Vérification du contenu de la réponse
    
    Validations:
    - Code HTTP 200
    - Content-Type: text/event-stream
    - Format SSE valide (data: {...})
    - Événements contenant role et content
    - Contenu non vide
    """
    # Parcourir tous les rôles avec config de test
    for app, role_name, test_config in stream_roles_with_tests:
        print(f"\n🧪 Testing streaming for role '{role_name}' in app '{app['app_name']}'")
        
        # Étape 1: Générer un chat_id dynamique
        chat_id = get_chat_id(app=app)
        
        # Créer la requête avec le chat_id généré
        request_data = {
            "chat_id": chat_id,
            "user_question": "Bonjour",
            "model_name": "gpt-4o"
        }
        
        # Étape 2: Appel API avec multipart/form-data
        response = api_client.post(
            endpoint="/get_answer_stream",
            app=app,
            data=request_data,
            stream=True
        )
    
        # Étape 3: Validation du code HTTP
        assert response.status_code == 200, (
            f"[{role_name}] Expected HTTP 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # Étape 4: Validation du Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "text/event-stream" in content_type, (
            f"[{role_name}] Expected text/event-stream, got {content_type}"
        )
        
        # Étape 5: Parser les événements SSE
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
        
        # Étape 6: Validation métier - Au moins un événement reçu
        assert len(sse_events) > 0, (
            f"[{role_name}] No SSE events received from streaming response"
        )
        
        # Étape 7: Validation métier - Structure des événements
        for idx, event in enumerate(sse_events):
            if "raw" not in event:
                # Événements structurés doivent avoir role/content OU event_type/answer
                has_legacy_format = "role" in event or "content" in event
                has_new_format = "event_type" in event or "answer" in event
                assert has_legacy_format or has_new_format, (
                    f"[{role_name}] Event {idx}: missing expected fields. Event: {event}"
                )
                
                # Vérifier le contenu selon le format
                content = event.get("content") or event.get("answer")
                if content is not None:
                    assert isinstance(content, str), (
                        f"[{role_name}] Event {idx}: content/answer must be a string"
                    )
        
        # Étape 8: Validation métier - Extraire le contenu complet
        full_content = ""
        for event in sse_events:
            # Supporter les deux formats: content (legacy) et answer (nouveau)
            content = event.get("content") or event.get("answer") or ""
            if content:
                full_content += content
        
        assert len(full_content) > 0, (
            f"[{role_name}] No content received from chatbot"
        )
        
        print(f"   ✅ Role '{role_name}' test passed:")
        print(f"      - App: {app['app_name']}")
        print(f"      - Chat ID: {chat_id}")
        print(f"      - Question: {request_data['user_question']}")
        print(f"      - Model: {request_data.get('model_name', 'default')}")
        print(f"      - Engine: {request_data.get('engine', 'default')}")
        print(f"      - Reasoning: {request_data.get('reasoning_level', 'default')}")
        print(f"      - SSE events received: {len(sse_events)}")
        print(f"      - Total content length: {len(full_content)} chars")
        print(f"      - Content preview: {full_content[:100]}...")


def test_get_answer_stream_missing_params(
    api_client,
    stream_app,
    get_chat_id
):
    """
    Test avec paramètres manquants.
    
    Validations:
    - Code HTTP 400 (Bad Request)
    - Message d'erreur présent
    """
    # Générer un chat_id
    chat_id = get_chat_id(app=stream_app)
    
    # Requête sans user_question (requis)
    invalid_request = {
        "chat_id": chat_id
        # user_question manquant
    }
    
    response = api_client.post(
        endpoint="/get_answer_stream",
        app=stream_app,
        data=invalid_request
    )
    
    assert response.status_code == 400, (
        f"Expected HTTP 400 for missing user_question, got {response.status_code}"
    )
    
    # Vérifier qu'une erreur est retournée
    try:
        json_response = response.json()
        assert "errors" in json_response or "error" in json_response, (
            "Expected error message in response"
        )
        assert json_response.get("success") == False, (
            "Expected success=False in error response"
        )
    except Exception:
        # Peut être du texte brut
        assert len(response.text) > 0, "Expected error message"
    
    print(f"\n✅ Missing params test passed: HTTP 400 returned")


def test_get_answer_stream_without_chat_id(
    api_client,
    stream_app
):
    """
    Test sans chat_id (requis).
    
    Validations:
    - Code HTTP 400 (Bad Request)
    - Message d'erreur présent
    """
    # Requête sans chat_id (requis)
    invalid_request = {
        "user_question": "What is Rexel?"
        # chat_id manquant
    }
    
    response = api_client.post(
        endpoint="/get_answer_stream",
        app=stream_app,
        data=invalid_request
    )
    
    assert response.status_code == 400, (
        f"Expected HTTP 400 for missing chat_id, got {response.status_code}"
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
    
    print(f"\n✅ Missing chat_id test passed: HTTP 400 returned")


def test_get_answer_stream_with_model_parameters(
    api_client,
    stream_app,
    get_chat_id
):
    """
    Test avec paramètres de modèle optionnels (model_name, engine, reasoning_level).
    
    Validations:
    - Code HTTP 200
    - Réponse en streaming
    - Contenu valide
    """
    # Générer un chat_id
    chat_id = get_chat_id(app=stream_app)
    
    # Requête avec tous les paramètres optionnels
    request_data = {
        "chat_id": chat_id,
        "user_question": "Bonjour",
        "model_name": "gpt-4o",
        "engine": "gpt-5-mini",
        "reasoning_level": "low"
    }
    
    response = api_client.post(
        endpoint="/get_answer_stream",
        app=stream_app,
        data=request_data,
        stream=True
    )
    
    assert response.status_code == 200, (
        f"Expected HTTP 200, got {response.status_code}"
    )
    
    # Vérifier le Content-Type
    content_type = response.headers.get("Content-Type", "")
    assert "text/event-stream" in content_type, (
        f"Expected text/event-stream, got {content_type}"
    )
    
    # Parser les événements SSE
    sse_events = []
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            data_str = line[6:]
            try:
                event_data = json.loads(data_str)
                sse_events.append(event_data)
            except json.JSONDecodeError:
                sse_events.append({"raw": data_str})
    
    # Valider qu'on a reçu des événements
    assert len(sse_events) > 0, "No SSE events received"
    
# Extraire le contenu (supporter les deux formats: content et answer)
    full_content = ""
    for event in sse_events:
        content = event.get("content") or event.get("answer") or ""
        if content:
            full_content += content
    
    assert len(full_content) > 0, "No content received from chatbot"
    
    print(f"\n✅ Model parameters test passed:")
    print(f"   - Chat ID: {chat_id}")
    print(f"   - Model: {request_data['model_name']}")
    print(f"   - Engine: {request_data['engine']}")
    print(f"   - Reasoning: {request_data['reasoning_level']}")
    print(f"   - Events: {len(sse_events)}")
    print(f"   - Content length: {len(full_content)} chars")


def test_get_answer_stream_all_configured_roles(
    api_client,
    stream_roles_with_tests,
    get_chat_id
):
    """
    Test avec tous les rôles configurés dans roles_test.
    
    Validations:
    - Tous les rôles configurés sont testés
    - Chaque rôle retourne une réponse valide (200 ou 403/400)
    """
    tested_count = 0
    
    for app, role_name, test_config in stream_roles_with_tests:
        stream_question = test_config.get("stream_question")
        
        if not stream_question:
            print(f"⚠️  Skipping {role_name}: no stream_question in roles_test")
            continue
        
        # Générer un chat_id dynamique pour chaque test
        chat_id = get_chat_id(app=app)
        request_data = {
            "chat_id": chat_id,
            "user_question": "Bonjour",
            "model_name": "gpt-4o"
        }
        
        response = api_client.post(
            endpoint="/get_answer_stream",
            app=app,
            data=request_data,
            stream=True
        )
        
        # Accepter 200 (succès) ou 403 (non autorisé) ou 400 (params invalides)
        assert response.status_code in [200, 403, 400], (
            f"Unexpected status {response.status_code} for "
            f"role={role_name}, app={app['app_name']}"
        )
        
        if response.status_code == 200:
            # Vérifier que c'est du streaming
            content_type = response.headers.get("Content-Type", "")
            assert "text/event-stream" in content_type or "application/json" in content_type
        
        tested_count += 1
        print(f"   ✅ {role_name} ({stream_question[:30]}...): HTTP {response.status_code}")
    
    print(f"\n✅ All configured streaming roles tested: {tested_count} role(s)")
