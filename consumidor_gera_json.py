# Consumidor da fila 'fila_operacoes_arquivos_local'
import pika
import msr.utils as util
from tqdm import tqdm
import time
from msr.dao import Repository, Repositories
import os
import json

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

def user_directory(path_repositories, user_id):
    user_path = path_repositories + '/' + str(user_id)
    if os.path.exists(user_path):
        return user_path
    else: 
        os.makedirs(user_path)
        return user_path  

def save_dictionary_in_json_file(name, user_id, my_dictionary, path_repositories): 
    try: 
        singleName = name + ".json"
        #Create the user directory if not existe
        temp_path = user_directory(path_repositories, user_id)
        fileName =  temp_path + '/' + singleName
        with open(fileName, 'w', encoding="utf-8") as jsonFile:
            json.dump(my_dictionary, jsonFile)
        print(f'The file {singleName} was saved with success!')
    except Exception as e:
        print(f'Error when try to save the json file: {e}')

def gerar_arquivos_json(user, repositorio, nome_repositorio, my_json):
    try:
        my_dictionary = json.loads(my_json)
        save_dictionary_in_json_file(nome_repositorio, user, my_dictionary, util.Constants.PATH_REPOSITORIES)
        print(f'Arquivo JSON Repositório {repositorio} gerado com sucesso na área do usuário: {user}!')
        status = 'Analisado'
        atualizar_status_no_banco(user, repositorio, status)
    except Exception as ex:
        print(f'Erro: {str(ex)}')

def generate_file_callback(ch, method, properties, body):
    body = body.decode('utf-8')
    if 'user' in body:
        try:
            user, repositorio, nome_repositorio, status, my_json = util.parser_body_com_json(body)
            gerar_arquivos_json(user, repositorio, nome_repositorio, my_json)
        except Exception as ex:
            print(f'Erro: {str(ex)}')     
 
channel_to_generate_file.basic_consume(my_fila1, generate_file_callback, auto_ack=True)
 
print(' [*] Waiting for messages to generate JSON file from repository. To exit press CTRL+C')
channel_to_generate_file.start_consuming()