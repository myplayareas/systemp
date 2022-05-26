import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                        datefmt='%d/%m/%Y %H:%M:%S', filename='my_app_produtor_clona_repositorio.log', filemode='w')

def parser_body(body):
    user = ''
    repositorio = ''
    nome_repositorio = ''
    status = ''
    try:
        str_temp = body.split(',')
        user = str_temp[0].split('=')[1]
        repositorio = str_temp[1].split('=')[1] 
        status = str_temp[2].split('=')[1]      
        separa_ponto = repositorio.split('.')
        nome_repositorio_temp = separa_ponto[1]
        nome_repositorio = nome_repositorio_temp.split('/')[-1]
    except Exception as e:
        print(f'Error parser body - {e}')
        logging.error("Exception occurred", exc_info=True)
    return user, repositorio, nome_repositorio, status

def parser_body_com_json(body):
    user = ''
    repositorio = ''
    nome_repositorio = '' 
    status = ''
    my_json = ''
    try: 
        str_temp = body.split('#')
        user = str_temp[0].split('=')[1]
        repositorio = str_temp[1].split('=')[1] 
        status = str_temp[2].split('=')[1] 
        my_json = str_temp[3].split('=')[1]     
        separa_ponto = repositorio.split('.')
        nome_repositorio_temp = separa_ponto[1]
        nome_repositorio = nome_repositorio_temp.split('/')[-1]
    except Exception as e:
        print(f'Erro: {str(e)}')
        logging.error("Exception occurred", exc_info=True)
    return user, repositorio, nome_repositorio, status, my_json

def parser_body_com_json_metrica(body):
    user = ''
    repositorio = ''
    nome_repositorio = '' 
    status = ''
    metrica = ''
    my_json = ''
    try: 
        str_temp = body.split('#')
        user = str_temp[0].split('=')[1]
        repositorio = str_temp[1].split('=')[1] 
        status = str_temp[2].split('=')[1] 
        metrica = str_temp[3].split('=')[1]
        my_json = str_temp[4].split('=')[1]     
        separa_ponto = repositorio.split('.')
        nome_repositorio_temp = separa_ponto[1]
        nome_repositorio = nome_repositorio_temp.split('/')[-1]
    except Exception as e:
        print(f'Erro: {str(e)}')
        logging.error("Exception occurred", exc_info=True)
    return user, repositorio, nome_repositorio, status, metrica, my_json

def enfilera_pedido_msg(canal, fila, usuario, repositorio, status, tipo):
    msg1 = f'Conectando ao canal {canal} na fila {fila}'
    msg2 = f'Enviando o pedido de {tipo} do repositório {repositorio} do usuário {usuario}'
    print(msg1)
    print(msg2)
    logging.info(msg1) 
    logging.info(msg2)
    conteudo = 'user=' + usuario + ',' + 'repository=' + repositorio + ',' + 'status='+status
    canal.basic_publish(exchange='', routing_key=fila, body=conteudo)

def enfilera_pedido_msg_com_json(canal, fila, usuario, repositorio, status, tipo, resultado):
    msg1 = f'Conectando ao canal {canal} na fila {fila}'
    msg2 = f'Enviando o pedido de {tipo} do repositório {repositorio} do usuário {usuario}'
    print(msg1)
    print(msg2)
    logging.info(msg1) 
    logging.info(msg2)
    conteudo = 'user=' + usuario + '#' + 'repository=' + repositorio + '#' + 'status=' + status + '#' + 'resultado=' + resultado
    canal.basic_publish(exchange='', routing_key=fila, body=conteudo)

def enfilera_pedido_msg_com_json_metrica(canal, fila, usuario, repositorio, status, tipo, metrica, resultado):
    msg1 = f'Conectando ao canal {canal} na fila {fila}'
    msg2 = f'Enviando o pedido de {tipo} do repositório {repositorio} do usuário {usuario}, metríca: {metrica}'
    print(msg1)
    print(msg2)
    logging.info(msg1) 
    logging.info(msg2)
    conteudo = 'user=' + usuario + '#' + 'repository=' + repositorio + '#' + 'status=' + status + '#' + 'metrica=' + metrica + '#' + 'resultado=' + resultado
    canal.basic_publish(exchange='', routing_key=fila, body=conteudo)

def pega_nome_repositorio(url):
    lista = []
    try: 
        temp = url.split('/')
        nome_com_extensao = ''
        for each in temp:
            if '.git' in each:
                nome_com_extensao = each
        lista = nome_com_extensao.split('.')
    except Exception as e:
        print(f'Error parser body - {e}')
        logging.error("Exception occurred", exc_info=True)
    return lista[0]

class Constants:
    PATH_MYADMIN = os.path.abspath(os.getcwd())
    PATH_MYAPP = PATH_MYADMIN + '/msr'
    PATH_STATIC = PATH_MYADMIN + '/msr/static'
    PATH_IMG = PATH_MYADMIN + '/msr/static/img'
    PATH_JSON = PATH_MYADMIN + '/msr/static/json'
    PATH_UPLOADS = PATH_MYADMIN + '/msr/static/uploads'
    PATH_REPOSITORIES = PATH_MYADMIN + '/msr/static/repositories'