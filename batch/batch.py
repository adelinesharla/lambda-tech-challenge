import psycopg2
import boto3
import os
from botocore.exceptions import ClientError

def conectar_aurora(hostname, database, user, password):
    """Conecta ao banco de dados Aurora."""
    try:
        conn = psycopg2.connect(
            host=hostname, database=database, user=user, password=password
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao Aurora: {e}")
        raise e

def consultar_cpfs(conn):
    """Consulta os CPFs dos usuários no banco de dados."""
    try:
        cur = conn.cursor()
        cur.execute("SELECT cpf FROM users") 
        cpfs = [row[0] for row in cur.fetchall()]
        return cpfs
    except Exception as e:
        print(f"Erro ao consultar CPFs: {e}")
        raise e

def criar_conta_cognito(cpf, user_pool_id):
    """Cria uma conta no Cognito."""
    try:
        client = boto3.client('cognito-idp')
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=cpf
        )
        print(f"Conta criada para CPF: {cpf}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            print(f"CPF já existe: {cpf}")
        else:
            print(f"Erro ao criar conta para CPF {cpf}: {e}")

def main():
    # Configuração do banco de dados
    hostname = os.environ['AURORA_HOSTNAME']
    database = os.environ['AURORA_DATABASE']
    user = os.environ['AURORA_USER']
    password = os.environ['AURORA_PASSWORD']

    # Configuração do Cognito
    user_pool_id = os.environ['COGNITO_USER_POOL_ID']

    try:
        conn = conectar_aurora(hostname, database, user, password)
        cpfs = consultar_cpfs(conn)

        for cpf in cpfs:
            criar_conta_cognito(cpf, user_pool_id)

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()