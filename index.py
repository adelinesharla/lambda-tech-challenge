import json
import boto3
import os
from botocore.exceptions import ClientError

class Autenticacao:
    def autenticar(self, cpf: str) -> bool:
        raise NotImplementedError()
    
class CognitoAutenticacao(Autenticacao):
    def __init__(self, user_pool_id: str):
        self.client = boto3.client('cognito-idp')
        self.user_pool_id = user_pool_id

    def autenticar(self, cpf: str) -> bool:
        try:
            self.client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=cpf
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                return False
            else:
                raise e

def handler(event, context):
    cpf = event['headers'].get('cpf')
    if not cpf:
        return {
            'statusCode': 400,
            'body': json.dumps('CPF não fornecido no cabeçalho')
        }

    if not validar_cpf(cpf):
        return {
            'statusCode': 400,
            'body': json.dumps('CPF inválido')
        }

    try:
        user_pool_id = os.environ['COGNITO_USER_POOL_ID']
        auth = CognitoAutenticacao(user_pool_id)

        if auth.autenticar(cpf):
            return {
                'statusCode': 200,
                'body': json.dumps('Autenticação bem-sucedida')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Usuário não encontrado')
            }

    except Exception as e:
        print("Erro ao autenticar usuário:", e)
        return {
            'statusCode': 500,
            'body': json.dumps('Erro interno do servidor')
        }

        
def validar_cpf(cpf):
    """
    Valida um CPF brasileiro.

    Args:
        cpf: O CPF a ser validado, como uma string de 11 dígitos numéricos.

    Returns:
        True se o CPF for válido, False caso contrário.
    """

    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return digito1 == int(cpf[9]) and digito2 == int(cpf[10])