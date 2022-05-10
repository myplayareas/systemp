# Consumidor e Produtor
# Consumidor da fila 'fila_status_banco'
# Produtor na fila 'fila_analise_commits'

import pika
import msr.utils as util
from msr.dao import Repository, Repositories

# Collection to manipulate repositories in data base
repositoriesCollection = Repositories()
 
rabbitmq_broker_host = 'localhost'
my_fila1 = 'fila_status_banco'
my_fila2 = 'fila_analise_commits'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_broker_host))

channel_to_update_db = connection.channel() 
channel_to_update_db.queue_declare(queue=my_fila1, durable=True)

channel_to_analysis = connection.channel()
channel_to_analysis.queue_declare(queue=my_fila2, durable=True)

def atualizar_status_no_banco(user, repositorio, status):
    print(f'Atualiza o status {status} do {repositorio} no banco na area do usuario: {user}')
    nome_repositorio = util.pega_nome_repositorio(repositorio)
    repositoriesCollection.update_repository_by_name(nome_repositorio, user, 1)

def update_db_callback(ch, method, properties, body):
    body = body.decode('utf-8')
    if 'user' in body:
        try:
            user, repositorio, nome_repositorio, status = util.parser_body(body)
            atualizar_status_no_banco(user, repositorio, status)
            print(f'Repositório do {nome_repositorio} atualizado no banco com status {status} com sucesso!')
            # 4.2. Enfilera pedido de análise de commits do repositório (14) (produtor)
            msg_analysis_db_repositorio(canal=channel_to_update_db, fila=my_fila2, usuario=user, repositorio=repositorio, status='Em analise')
        except Exception as ex:
            print(f'Erro: {str(ex)}')     

# 4.1. Dispara uma solicitação para analisar os commits do repositório (13)
def msg_analysis_db_repositorio(canal=channel_to_update_db, fila=my_fila2, usuario='', repositorio='', status=''):
    tipo = 'analysis'
    util.enfilera_pedido_msg(canal, fila, usuario, repositorio, status, tipo)

channel_to_update_db.basic_consume(my_fila1, update_db_callback, auto_ack=True)
 
print(' [*] Waiting for messages to update in DB. To exit press CTRL+C')
channel_to_update_db.start_consuming()