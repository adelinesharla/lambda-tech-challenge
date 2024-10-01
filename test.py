import pytest
import json
from index import handler
from botocore.exceptions import ClientError



# /generate mock cognito
@pytest.fixture
def mock_cognito(monkeypatch):
    def mock_admin_get_user(UserPoolId, Username):
        if Username == "75223055780":
            return {"UserAttributes": []}
        else:
            raise ClientError({"Error": {"Code": "UserNotFoundException"}}, "admin_get_user")
    monkeypatch.setattr("index.CognitoAutenticacao.client.admin_get_user", mock_admin_get_user)

# /generate test cases
@pytest.mark.parametrize("cpf, expected_status_code, expected_body", [
    ("75223055780", 200, '{"message": "Autenticação bem-sucedida"}'),
    ("12345678901", 400, '{"message": "CPF inválido"}'),
    ("11111111111", 400, '{"message": "CPF inválido"}'),
    ("123456789012", 400, '{"message": "CPF inválido"}'),
    ("abc123456789", 400, '{"message": "CPF inválido"}'),
    (None, 400, '{"message": "CPF não fornecido no cabeçalho"}'),
])

def test_handler(mock_cognito, cpf, expected_status_code, expected_body):
    payload = {
        "headers": {
            "cpf": cpf
        }
    }
    response = handler(payload, None)
    assert response['statusCode'] == expected_status_code
    assert response['body'] == json.dumps(expected_body)

def test_authentication():
    payload = {
        "headers": {
            "cpf": "75223055780"
        }
    }
    response = handler(payload, None)
    assert response['statusCode'] == 200
    assert response['body'] == '{"message": "Autenticação bem-sucedida"}'

def test_invalid_cpf():
    payload = {
        "headers": {
            "cpf": "12345678901"
        }
    }
    response = handler(payload, None)
    assert response['statusCode'] == 400
    assert response['body'] == '{"message": "CPF inválido"}'

def test_missing_cpf():
    payload = {
        "headers": {}
    }
    response = handler(payload, None)
    assert response['statusCode'] == 400
    assert response['body'] == '{"message": "CPF não fornecido no cabeçalho"}'