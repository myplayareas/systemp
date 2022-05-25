import os
import pika
import json
import logging
from enum import Enum
import msr.utils as util
from pydriller import Repository
from subprocess import check_output

rabbitmq_broker_host = 'localhost'
my_fila1 = 'fila_analisador'
my_fila2 = 'fila_geracao_json'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_broker_host, heartbeat=0))

channel_to_analysis = connection.channel() 
channel_to_analysis.queue_declare(queue=my_fila1, durable=True)

channel_to_generate_json = connection.channel()
channel_to_generate_json.queue_declare(queue=my_fila2, durable=True)

class Type(Enum):
  DIR = 0
  FILE = 1

class HeatmapMetric(Enum):
  FREQUENCY = 0
  COMPLEXITY = 1
  LOC_CHANGES = 2
  COMPOSITION = 3

class Node:
  def __init__(self, name, loc, heatmap, node_type, depth, children = []):
    self.name = name
    self.loc = loc
    self.node_type = node_type
    self.depth = depth
    self.children = children
    self.parent = None
    self.heatmap = heatmap
  
  def append_node(self, node):
    node.parent = self
    self.children.append(node)
    
def calculate_loc_tree(node):
  loc = 0
  for each in node.children:
    loc += each.loc + calculate_loc_tree(each)
  if len(node.children) > 0:
    node.loc = loc
  if node.parent is not None:
    return loc

def create_tree(name, list_of_files_and_directories, list_locs_of_files, dict_of_heatmap_metric):

  root = Node(name=name,loc=0, heatmap=1, node_type=Type.DIR, depth=0, children=[])

  nodes = [root]

  for key in list_of_files_and_directories:
    last_name = key.split('/')[-1]
    depth = key.count('/')
    loc = 0
    heatmap = 0

    if os.path.isdir(key):
      key_type = Type.DIR
      heatmap = 0
    else:
      key_type = Type.FILE
      if key in list_locs_of_files:
        loc = list_locs_of_files[key]
      if last_name in dict_of_heatmap_metric:
        heatmap = dict_of_heatmap_metric[last_name]

    if depth != len(nodes):
      diff = abs(depth - len(nodes))
      if depth < len(nodes):
        for i in range(0, diff):
          nodes.pop()
      else:
        nodes.append(node)

    node = Node(name=last_name, loc=loc, heatmap=heatmap, node_type=key_type, depth=depth, children=[])

    if len(nodes) > 0:
      nodes[len(nodes) - 1].append_node(node)

  calculate_loc_tree(root)
  return root

def should_ignore(name):
  list_of_files_and_directories_to_ignore = ['.git']
  return True in [i in name for i in list_of_files_and_directories_to_ignore]

def count_lines_of_code_of_files(path_repositorio):
  os.system(f"find {path_repositorio} | xargs wc -l > locfiles.txt")
  with open("locfiles.txt", "r") as locfiles:
    return locfiles.readlines()[:-1]

def get_list_of_files_and_directories(path_repositorio, name):
  print(path_repositorio)
  list_of_files_and_directories = check_output(f"cd {path_repositorio} && tree -i -f", shell=True).decode("utf-8").splitlines()
  return [each.replace('./', name + '/') for each in list_of_files_and_directories][1:-2]

def get_list_of_files_loc(name):
    list_locs_of_files = {}

    for each in count_lines_of_code_of_files(name):
        if not should_ignore(each):
            elements = each.split(' ') 
            if(elements[-1] != "" and elements[-2] != ""):
                list_locs_of_files[elements[-1].replace('\n', '')] = int(elements[-2])
    return list_locs_of_files

def get_list_of_commits(path_repositorio):
  limit = 100
  commits = []
  for commit in Repository(path_repositorio, order='reverse').traverse_commits():
    if limit == 0:
      break
    commits.append(commit)
    limit -= 1
  return commits

def get_files_frequency_in_commits(path_repositorio):
  file_frequency = {}
  for commit in get_list_of_commits(path_repositorio):
    for modified_file in commit.modified_files:
      if modified_file.filename in file_frequency.keys():
        file_frequency[modified_file.filename] += 1
      else:
        file_frequency[modified_file.filename] = 1
  return file_frequency

def get_number_of_lines_of_code_changes_in_commits(path_repositorio):
  number_of_line_changes = {}
  for commit in get_list_of_commits(path_repositorio):
    for modified_file in commit.modified_files:
      if modified_file.filename in number_of_line_changes.keys():
        number_of_line_changes[modified_file.filename] += modified_file.added_lines + modified_file.deleted_lines
      else:
        number_of_line_changes[modified_file.filename] = modified_file.added_lines + modified_file.deleted_lines
  return number_of_line_changes

def get_files_cyclomatic_complexity_in_commits(path_repositorio):
  complexity = {}
  for commit in get_list_of_commits(path_repositorio):
    for modified_file in commit.modified_files:
      complexity[modified_file.filename] = 0 if modified_file.complexity is None else modified_file.complexity
  return complexity

def get_composition(path_repositorio):
  file_frequency = get_files_frequency_in_commits(path_repositorio)
  number_of_line_changes = get_number_of_lines_of_code_changes_in_commits(path_repositorio)
  complexity = get_files_cyclomatic_complexity_in_commits(path_repositorio)
  composition = {}
  for key, _ in file_frequency.items():
    fc = file_frequency[key]
    ml = number_of_line_changes[key]
    cc = complexity[key]
    composition[key] = fc*ml*cc
  return composition

def create_json_object(node):
  return {
    "name": node.name,
    "type": node.node_type.name,
    "weight": node.loc,
    "depth": node.depth,
    "heatmap": node.heatmap,
    "children": []
  }

def traverse(node):
  children = []
  for child in node.children:
    node = create_json_object(child)
    children.append(node)
    node["children"] = traverse(child)
  return children

def create_json(root):
  json_output = create_json_object(root)
  json_output["children"] = traverse(root)
  return json.dumps(json_output)

def analisar_repositorio(user, repositorio, nome_repositorio, status):
    path_repositorio = util.Constants.PATH_REPOSITORIES + '/' + user + '/' + nome_repositorio
    functions = [get_files_frequency_in_commits, get_files_cyclomatic_complexity_in_commits, get_number_of_lines_of_code_changes_in_commits, get_composition]
    for metric in HeatmapMetric:
        dict_of_heatmap_metric = functions[metric.value](path_repositorio)
        root = create_tree(nome_repositorio,  get_list_of_files_and_directories(path_repositorio, nome_repositorio), get_list_of_files_loc(nome_repositorio), dict_of_heatmap_metric)
        json = create_json(root)
        msg_generate_file_repositorio(canal=channel_to_generate_json, fila=my_fila2, usuario=user, repositorio=repositorio, status=status, metrica=str.lower(metric.name), resultado=json)

def analise_callback(ch, method, properties, body): 
    body = body.decode('utf-8')
    if 'user' in body:
        try:
            user, repositorio, nome_repositorio, status = util.parser_body(body)
            analisar_repositorio(user, repositorio, nome_repositorio, status)         
            msg1 = f'Análise do repositório {repositorio} concluida!' 
            print(msg1)
            logging.info(msg1)
        except Exception as ex:
            print(f'Erro: {str(ex)}')     

def msg_generate_file_repositorio(canal=channel_to_generate_json, fila=my_fila2, usuario='', repositorio='', status='', resultado=''):
    tipo = 'gerar arquivo JSON'
    util.enfilera_pedido_msg_com_json(canal, fila, usuario, repositorio, status, tipo, resultado)

channel_to_analysis.basic_consume(my_fila1, analise_callback, auto_ack=True)

print(' [*] Waiting for messages to analysis queue. To exit press CTRL+C') 
channel_to_analysis.start_consuming()