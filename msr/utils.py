import os

class Constants:
    PATH_MYADMIN = os.path.abspath(os.getcwd())
    PATH_MYAPP = PATH_MYADMIN + '/msr'
    PATH_STATIC = PATH_MYADMIN + '/msr/static'
    PATH_IMG = PATH_MYADMIN + '/msr/static/img'
    PATH_JSON = PATH_MYADMIN + '/msr/static/json'
    PATH_UPLOADS = PATH_MYADMIN + '/msr/static/uploads'
    PATH_REPOSITORIES = PATH_MYADMIN + '/msr/static/repositories'