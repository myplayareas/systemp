# Consumidor da fila 'fila_operacoes_arquivos_local'
import os
import json
import pika
import logging
import msr.utils as util
from msr.dao import Repositories

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                datefmt='%d/%m/%Y %H:%M:%S', filename='logs/treemap/my_app_consumidor_gera_json.log', filemode='w')

# Collection to manipulate repositories in data base
repositoriesCollection = Repositories()
 
rabbitmq_broker_host = 'localhost'
my_fila1 = 'fila_geracao_json'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_broker_host, heartbeat=0))

channel_to_generate_json = connection.channel()
channel_to_generate_json.queue_declare(queue=my_fila1, durable=True)

def atualizar_status_no_banco(user, repositorio, status):
    msg1 = f'Atualiza o status {status} do {repositorio} no banco na area do usuario: {user}' 
    msg2 = f'Status {status} do {repositorio} salvo no banco com sucesso!' 
    try:
        print(msg1)
        logging.info(msg1)
        nome_repositorio = util.pega_nome_repositorio(repositorio)
        repositoriesCollection.update_repository_by_name(nome_repositorio, user, 2)
        print(msg2)
        logging.info(msg2)
    except Exception as e:
        print(f'Erro: {str(e)}')
        logging.error("Exception occurred", exc_info=True)

def user_directory(path_repositories, user_id, name):
    user_path = path_repositories + '/' + str(user_id) + '/' + name
    if os.path.exists(user_path):
        return user_path
    else: 
        os.makedirs(user_path)
        return user_path  

def save_dictionary_in_json_file(name, user_id, my_dictionary, metrica, path_repositories): 
    try: 
        singleName = metrica + ".json"
        #Create the user directory if not existe
        temp_path = user_directory(path_repositories, user_id, name)
        fileName =  temp_path + '/' + singleName
        msg1 = f'Saving the file {fileName}...' 
        print(msg1)
        logging.info(msg1)
        with open(fileName, 'w', encoding="utf-8") as jsonFile:
            json.dump(my_dictionary, jsonFile)
        msg2 = f'The file {fileName} was saved with success!' 
        print(msg2)
        logging.info(msg2)
    except Exception as e:
        print(f'Error when try to save the json file: {e}')
        logging.error("Exception occurred", exc_info=True)

def gerar_arquivos_json(user, repositorio, nome_repositorio, metrica, my_json):
    try:
        my_dictionary = json.loads(my_json)
        save_dictionary_in_json_file(nome_repositorio, user, my_dictionary, metrica, util.Constants.PATH_REPOSITORIES)
        status = 'Analisado'
        atualizar_status_no_banco(user, repositorio, status)
    except Exception as ex:
        print(f'Erro: {str(ex)}')
        logging.error("Exception occurred", exc_info=True)

def generate_file_callback(ch, method, properties, body):
    body = body.decode('utf-8')
    if 'user' in body:
        try:
            user, repositorio, nome_repositorio, status, metrica, my_json = util.parser_body_com_json_metrica(body)
            gerar_arquivos_json(user, repositorio, nome_repositorio, metrica, my_json)
        except Exception as ex:
            print(f'Erro generate_file_callback: {str(ex)}')     
            logging.error("Exception occurred", exc_info=True)
 
channel_to_generate_json.basic_consume(my_fila1, generate_file_callback, auto_ack=True)
 
print(' [*] Waiting for messages to generate Treemap JSON file from repository. To exit press CTRL+C')
channel_to_generate_json.start_consuming()
