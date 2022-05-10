# Consumidor e Produtor
# Consumidor da fila 'fila_analise_commits'
# Produtor na fila 'fila_operacoes_arquivos_local'

import pika
import msr.utils as util
from tqdm import tqdm
import time
 
rabbitmq_broker_host = 'localhost'
my_fila1 = 'fila_analise_commits'
my_fila2 = 'fila_operacoes_arquivos_local'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_broker_host))

channel_to_analysis = connection.channel() 
channel_to_analysis.queue_declare(queue=my_fila1, durable=True)

channel_to_generate_file = connection.channel()
channel_to_generate_file.queue_declare(queue=my_fila2, durable=True)

def analisar_repositorio(user, repositorio):
    print(f'Faz a analise do {repositorio}, na area do usuario: {user}')
    for i in tqdm(range(5)):
        time.sleep(1)

def analise_callback(ch, method, properties, body):
    body = body.decode('utf-8')
    if 'user' in body:
        try:
            user, repositorio, nome_repositorio, status = util.parser_body(body)
            analisar_repositorio(user, repositorio)          
            print(f'Análise do repositório {repositorio} concluida!')
            # 5.8. Enfilera pedido de gerar arquivo JSON do repositório (20) (produtor)
            msg_generate_file_repositorio(canal=channel_to_generate_file, fila=my_fila2, usuario=user, repositorio=repositorio, status=status)
        except Exception as ex:
            print(f'Erro: {str(ex)}')     

# 5.7. Dispara uma solicitação para gerar o JSON com as respostas da análise do repositório (19)
def msg_generate_file_repositorio(canal=channel_to_generate_file, fila=my_fila2, usuario='', repositorio='', status=''):
    tipo = 'gerar arquivo JSON'
    util.enfilera_pedido_msg(canal, fila, usuario, repositorio, status, tipo)
 
channel_to_analysis.basic_consume(my_fila1, analise_callback, auto_ack=True)

print(' [*] Waiting for messages to analysis queue. To exit press CTRL+C') 
channel_to_analysis.start_consuming()