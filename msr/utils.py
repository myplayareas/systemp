import os

def parser_body(body):
    str_temp = body.split(',')
    user = str_temp[0].split('=')[1]
    repositorio = str_temp[1].split('=')[1] 
    status = str_temp[2].split('=')[1]      
    separa_ponto = repositorio.split('.')
    nome_repositorio_temp = separa_ponto[1]
    nome_repositorio = nome_repositorio_temp.split('/')[-1]
    return user, repositorio, nome_repositorio, status

def parser_body_com_json(body):
    str_temp = body.split('#')
    user = str_temp[0].split('=')[1]
    repositorio = str_temp[1].split('=')[1] 
    status = str_temp[2].split('=')[1] 
    my_json = str_temp[3].split('=')[1]     
    separa_ponto = repositorio.split('.')
    nome_repositorio_temp = separa_ponto[1]
    nome_repositorio = nome_repositorio_temp.split('/')[-1]
    return user, repositorio, nome_repositorio, status, my_json

def enfilera_pedido_msg(canal, fila, usuario, repositorio, status, tipo):
    print(f'Conectando ao canal {canal} na fila {fila}')
    print(f'Enviando o pedido de {tipo} do repositório {repositorio} do usuário {usuario}')
    conteudo = 'user=' + usuario + ',' + 'repository=' + repositorio + ',' + 'status='+status
    canal.basic_publish(exchange='', routing_key=fila, body=conteudo)

def enfilera_pedido_msg_com_json(canal, fila, usuario, repositorio, status, tipo, resultado):
    print(f'Conectando ao canal {canal} na fila {fila}')
    print(f'Enviando o pedido de {tipo} do repositório {repositorio} do usuário {usuario}')
    conteudo = 'user=' + usuario + '#' + 'repository=' + repositorio + '#' + 'status=' + status + '#' + 'resultado=' + resultado
    canal.basic_publish(exchange='', routing_key=fila, body=conteudo)

def pega_nome_repositorio(url):
    temp = url.split('/')
    nome_com_extensao = ''
    for each in temp:
        if '.git' in each:
          nome_com_extensao = each
    lista = nome_com_extensao.split('.')
    return lista[0]

class Constants:
    PATH_MYADMIN = os.path.abspath(os.getcwd())
    PATH_MYAPP = PATH_MYADMIN + '/msr'
    PATH_STATIC = PATH_MYADMIN + '/msr/static'
    PATH_IMG = PATH_MYADMIN + '/msr/static/img'
    PATH_JSON = PATH_MYADMIN + '/msr/static/json'
    PATH_UPLOADS = PATH_MYADMIN + '/msr/static/uploads'
    PATH_REPOSITORIES = PATH_MYADMIN + '/msr/static/repositories'