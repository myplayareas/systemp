# Consumidor da fila 'fila_operacoes_arquivos_local'
import pika
import msr.utils as util
from tqdm import tqdm
import time
from msr.dao import Repository, Repositories

# Collection to manipulate repositories in data base
repositoriesCollection = Repositories()
 
rabbitmq_broker_host = 'localhost'
my_fila1 = 'fila_operacoes_arquivos_local'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_broker_host))

channel_to_generate_file = connection.channel()
channel_to_generate_file.queue_declare(queue=my_fila1, durable=True)

def atualizar_status_no_banco(user, repositorio, status):
    print(f'Atualiza o status {status} do {repositorio} no banco na area do usuario: {user}')
    nome_repositorio = util.pega_nome_repositorio(repositorio)
    repositoriesCollection.update_repository_by_name(nome_repositorio, user, 2)

def gerar_arquivos_json(user, repositorio):
    try:
        for i in tqdm(range(3)):
            time.sleep(1)
        print(f'Arquivo JSON Repositório {repositorio} gerado com sucesso na área do usuário: {user}!')
        status = 'Analisado'
        atualizar_status_no_banco(user, repositorio, status)
    except Exception as ex:
        print(f'Erro: {str(ex)}')

def generate_file_callback(ch, method, properties, body):
    body = body.decode('utf-8')
    if 'user' in body:
        try:
            user, repositorio, nome_repositorio, status = util.parser_body(body)
            gerar_arquivos_json(user, repositorio)
        except Exception as ex:
            print(f'Erro: {str(ex)}')     
 
channel_to_generate_file.basic_consume(my_fila1, generate_file_callback, auto_ack=True)
 
print(' [*] Waiting for messages to generate JSON file from repository. To exit press CTRL+C')
channel_to_generate_file.start_consuming()