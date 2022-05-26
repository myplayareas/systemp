# systemp
Systemp...

Server1 - Application Server (Flask Web App)

Server2 - Message broker (RabbitMQ)

## 1. Installing requirement (Server1)

No Server1, prepare o ambiente virtual para logo depois rodar a aplicação flask principal. 

Clone o repositorio
```bash
git clone https://github.com/myplayareas/systemp.git
```

Vá para o diretório systemp
```bash
cd systemp
```

Virtual environment
```bash
python3 -m venv venv
```

Activate virtual environment
```bash
source venv/bin/activate
```

Install requirements
```bash
pip3 install -r requirements.txt
```

## 2. repositoryanalysis (Server2)
Repository Analysis - Permite a análise assíncrona de vários repositórios git na forma enfeiramento de pedidos.

Dado um repositório git o mesmo é salvo em banco e logo depois é clonado para permitir uma análise local. Ao final da análise do repositório gera um arquivo JSON com os resultados da análise.

Para o nosso exemplo, o Server2 será um container docker hospedado no Server1. Com isso, garanta que tenha o docker instalado e executando no Server1. 

### Para rodar o RabbitMQ com o docker, basta rodar a seguinte linha de comando:

No Server1 execute o seguinte comando: 
```
docker run --rm -p 5672:5672 -p 8080:15672 rabbitmq:3-management
```

No Server1, você pode acessar a web app do RabbitMQ via http://localhost:8080

Quando a aplicação do Server1 for executada, serão criadas as seguintes filas: 

fila_repositorio_local - Fila que organiza as solicitações para clonar os repositórios

fila_analise_commits - Fila que organiza as solicitações de análise dos repositórios

fila_operacoes_arquivo_local - Fila que organiza a geração de arquivos JSON contendo os resultados das análises de cada repositório

fila_status_banco - Fila que organiza as solicitações de atualização de status de cada repositório no banco

fila_analisador - Fila que organiza as solicitações de análises da treemap

fila_geracao_json - Fila que organiza as solicitações de geração de JSON (treemap/heatmap) de acordo com as métricas passadas

Entre com o usuário guest/guest para visualizar as operações do message broker em tempo real. 

### Para visualizar as mensagens de uma fila no RabbitMQ (Server2):

Acesse o container docker que está executando o Server2

```
rabbitmqadmin get queue=fila_operacoes_arquivos_local count=10
```

## 3. Run application (Server1)

To run the application, it is necessary to install all the modules and extensions mentioned above. In addition, you need to set the following environment variables:

For the Posix environment:
```bash
# Shell 1
export FLASK_APP=run.py && export FLASK_ENV=development
```
More details at [CLI Flask](https://flask.palletsprojects.com/en/2.0.x/cli/)

Run the application via CLI:
```bash
# Shell 1
flask run
```

### 3.1 Executando os produtores e consumidores

produtor da fila_repositorio_local - atualiza no banco e solicita clonagem - (produtor)
```
running in main.py
```

(Server1) - Consumidor da fila_repositorio_local e produtor da fila_status_banco - faz a clonagem e solicita atualização do BD - (consumidor e produtor)
```
# Shell 2
python3 consumidor_clona_repositorio.py
```

(Server1) - Consumidor da fila_status_banco e produtor da fila_analise_commits - atualiza o BD e solicita análise do repositório - (consumidor e produtor)
```
# Shell 3
python3 consumidor_atualiza_status_banco.py
```

(Server1) - Consumidor da fila_analise_commits e produtor da fila_operacoes_arquivos_local - analisa os commits do repositório e solicita gerar JSON - (consumidor e produtor)
```
# Shell 4
python3 consumidor_analisa_commits.py
```

(Server1) - Consumidor da fila_arquivos_local - Gera o arquivo JSON com os resultados da análise do repositório.
```
# Shell 5
python3 consumidor_gera_json.py 
```

(Server1) - O "agente" (consumidor/produtor) [analisador de repositório para treemap] analisa (consome da fila_analisador ) o repositório e depois dispara (produz msg para fila_geracao_json ) um pedido para gerar o arquivo json correspondente.
```
# Shell 6
python3 consumidor_treemap_analisador.py 
```
(Server1) - O "agente" (consumidor) [gerador de JSON para treemap] recebe (consome da fila_geracao_json ) o pedido e gera o JSON correspondente na pasta do usuário.
```
# Shell 7
python3 consumidor_treemap_gera_json.py
```
### 3.2 Chamando a aplicação web

http://localhost:5000