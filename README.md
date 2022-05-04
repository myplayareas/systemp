# systemp
Systemp

### Installing requiremnts 

Virtual environment
```bash
$python3 -m venv venv
```

Activate virtual environment
```bash
$source venv/bin/activate
```

Install requirements
```bash
pip3 install -r requirements.txt
```

### Run application

To run the application, it is necessary to install all the modules and extensions mentioned above. In addition, you need to set the following environment variables:

For the Posix environment:
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```
More details at [CLI Flask](https://flask.palletsprojects.com/en/2.0.x/cli/)

Run the application via CLI:
```bash
$flask run
```