from msr import app
from flask import render_template, redirect, url_for, flash
from msr.dao import Users, Repository, Repositories
from msr.forms import  RepositoryForm
from flask_login import login_required, current_user
import datetime
from functools import wraps
from werkzeug.exceptions import HTTPException, InternalServerError
from flask import current_app, request, abort
from msr import utils
from msr import produtor_clona_repositorio

# Lista da strings de repositorios
lista_de_repositorios = list()

# Collection to manipulate users in data base
usersCollection = Users()

# Collection to manipulate repositories in data base
repositoriesCollection = Repositories()

def repositorios_ja_existem(lista_de_repositorios, user_id):
    lista_de_repositorios_ja_existem = list()
    try: 
        for each in lista_de_repositorios:
            resultado = repositoriesCollection.query_repositories_by_name_and_user_id(pega_nome_repositorio(each), user_id)
            if len(resultado) > 0:
                lista_de_repositorios_ja_existem.append( resultado )
    except Exception as e:
        print(f'Erro ao consultar repositorio no banco: {e}')
    return lista_de_repositorios_ja_existem

@app.route("/criar", methods=["GET", "POST"])
@login_required
def criar_em_cadeia():
    """Create a new repository for the current user."""
    if request.method == "POST":
        error = None
        cadeia_de_repositorios = request.form["repositorios"]

        # Nenhum repositorio foi passado
        if len(cadeia_de_repositorios) == 0:
            error = "List of repositories is required."
            flash(error, 'danger')
            return render_template("repository/criar.html")
        else:
            lista_de_repositorios = cadeia_de_repositorios.split(",")
            testa_repositorios = repositorios_ja_existem(lista_de_repositorios, current_user.get_id() )

        # Checa se ja existe algum repositorio no banco
        if len(testa_repositorios) > 0: 
            lista = list()
            for each in testa_repositorios:
                lista.append(each[0].name)

            error = f'O(s) repositorio(s) {lista} já foi(forão) cadastrado(s) no banco!'
            flash(error, category='danger')
            return render_template("repository/criar.html")
        
        print(f'{utils.Constants.PATH_REPOSITORIES}')
        print(f'Salva as informacoes do {cadeia_de_repositorios} no banco de dados')
        message = "Repositório(s) criado(s) com sucesso!"
        flash(message, 'success')
        return redirect(url_for("msr_page"))

    return render_template('repository/criar.html')

@app.context_processor
def utility_processor():
    def status_repositorio(status):
        valor = ''
        try:
            lista_de_status = list()
            lista_de_status = ['Registered', 'Processing', 'Analysed']
            valor = lista_de_status[status]
        except Exception as e:
            print('Erro de status: valor ' + valor + ' - status:  ' + str(status) + ' - ' + str(e))
        return valor
    return dict(status_repositorio=status_repositorio)
    
@app.route("/repository/<int:id>/analysed", methods=["GET"])
@login_required
def visualizar_analise_repositorio(id):
    repositorio = repositoriesCollection.query_repository_by_id(id)
    link = repositorio.link
    name = repositorio.name
    creation_date = repositorio.creation_date
    analysis_date = repositorio.analysis_date
    status = repositorio.analysed

    relative_path = 'repositories' + '/' + str(current_user.get_id()) + '/' + name + '.json'
    relative_path_file_name = url_for('static', filename=relative_path)

    return render_template("repository/analisado.html", my_link=link, my_name=name, my_creation_date=creation_date,
                                my_analysis_date=analysis_date, my_status=status,
                                my_relative_path_file_name=relative_path_file_name)

def exist_repository_in_user(name, link, lista):
    checa = False
    if len(lista) > 0:
        for each in lista:
            if each.name == name or each.link == link:
                checa = True
    return checa

@app.route('/repository', methods=['GET', 'POST'])
@login_required
def repository_page():
    form = RepositoryForm()

    if form.validate_on_submit():
        name = form.name.data
        link = form.link.data

        list_user_repositories = repositoriesCollection.query_repositories_by_user_id(current_user.get_id())
        if not exist_repository_in_user(name, link, list_user_repositories):
            repository = Repository(name=name, link=link, creation_date=datetime.datetime.now(), 
                                            analysis_date=None, analysed=0, owner=current_user.get_id())
            repositoriesCollection.insert_repository(repository)
            produtor_clona_repositorio.msg_clona_repositorio(fila=produtor_clona_repositorio.my_fila, usuario=current_user.get_id(), 
                                                            repositorio=link, status='Registrado')
            flash(f'Repository {repository.name} saved with success!', category='success')
            return redirect(url_for('msr_page'))
        flash('Repository already exist!', category='danger')

    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with new repository: {err_msg}', category='danger')

    return render_template('repository/repository.html', form=form)  