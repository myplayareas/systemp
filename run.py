from msr import app
from msr import db, data_base
from msr.dao import User, Repository

CREATE_DB_EMPTY = False

try:
    if CREATE_DB_EMPTY:
        db.drop_all()
        db.create_all()
        print(f'Data base {data_base} created with success!!')
except Exception as e:
    print(f'Error creating {data_base} - {e}')

if __name__ == '__main__':
    app.run(debug=True)