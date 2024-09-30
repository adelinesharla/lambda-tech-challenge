import json
import boto3
import os
from botocore.exceptions import ClientError

def handler(event, context):
    """
    Função Lambda para autenticar um usuário com base no CPF, usando o Cognito.
    """

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
        client = boto3.client('cognito-idp')
        response = client.admin_get_user(
            UserPoolId=os.environ['COGNITO_USER_POOL_ID'],
            Username=cpf
        )

        user_attributes = response['UserAttributes']

        for attribute in user_attributes:
            if attribute['Name'] == 'cpf' and attribute['Value'] == cpf:
                return {
                    'statusCode': 200,
                    'body': json.dumps('Autenticação bem-sucedida')
                }

        return {
            'statusCode': 401,
            'body': json.dumps('CPF não corresponde ao usuário')
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            return {
                'statusCode': 404,
                'body': json.dumps('Usuário não encontrado')
            }
        else:
            print("Erro ao obter usuário no Cognito:", e)
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