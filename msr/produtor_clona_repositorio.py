# Produtor da fila 'fila_repositorio_local'
import pika
import msr.utils as util

rabbitmq_host = 'localhost'
my_fila = 'fila_repositorio_local'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))

channel_to_clone = connection.channel() 
channel_to_clone.queue_declare(queue=my_fila, durable=True)

# 2.2. Enfilera pedido de clonagem do repositório (6) (produtor)
def msg_clona_repositorio(canal=channel_to_clone, fila=my_fila, usuario='', repositorio='', status=''):
    tipo = 'clonagem'
    util.enfilera_pedido_msg(canal, fila, usuario, repositorio, status, tipo)