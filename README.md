# Knock Code Survey

Install python 3.7 and then create a virtualenv for local `pip` installation

```
virtualenv -c python3 py3
```

Star the virtual environment

```
source py3/bin/activate   
```
  
install packages (only need to run once)

```
pip install -r requirements
```

Create migrations (only need to run when changing the models)

```
python manage.py makemigrations survey
```

Migrate (run after making any new migrations)

```
python manage.py migrate
```


Start the server

```
python manage.py runserver
```

Go to the following URL in your browser

[http://127.0.0.1:8000/root](http://127.0.0.1:8000/root)

This will create a root entry to start the survey, click start and follow directions.

If you get an error screen, you need to complete the survey using a mobile device. To simulate a mobile device use the development tools in the browser and select the mobile view. 

Data is stored to the sqlite database file in the home directory.

