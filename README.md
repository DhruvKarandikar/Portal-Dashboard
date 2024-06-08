Portal Dashboard Backend



Installation steps:

step 1: Use git clone to make this project into your respective project
step 2: Connect your local database with postgres to the Django Project 

NOTE: Download Postgres into your local device to link it with project

IMPORTANT

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': your database name ,
        'USER': "postgres",
        'PASSWORD': password ,
        'HOST': your host name,
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
    }
}

step 3: After connecting to the database. Use this commands to use API's commands:

Command will create the virtual environment for project

        python -m venv env

Use this command to activate environment

Windows:

        CMD: .\env\Scripts\activate

Mac OS:

        src ~/env/Scripts/activate

Download the requirements file
        
        pip install -r requirements.txt

Command for migrating the database into your local computer

        python manage.py migrate

Running the server

        python manage.py runserver

step 4: After connecting to the server and running the project you will get the local host link in terminal having 8000 port.
You will see a page with more extension to the URL's: 
Kindly go to the URL's which are swagger basis as the postman will do the same as the swagger:

NOTE: This link will make you to interactive site where API are interactive if postman not installed.
Recommended Swagger as it will allow you to see the json format. In postman you have to send 
the API and see the JSON from the code.
        
        Swagger in browser: 
        http://127.0.0.1:8000/v1/social_management/swagger/
        
        Postman: 
        http://127.0.0.1:8000/v1/social_management/{user API name here to interact it with specific url}
