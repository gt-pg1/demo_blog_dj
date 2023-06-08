

# Description

This web application is built with Django and serves as a platform for creating and publishing user-generated content, such as articles, as well as commenting on those articles.

# Key Features

 1. User registration/authentication 
 2. Creation, editing, and publishing of articles 
 3. Adding and deleting comments to articles 
 4. Changing the publication status of articles
 5. Updating user activity upon specific actions

# Technical Details

## Models:

The project includes the following main models:

1. **User**: Django user model, modified to make email the primary unique identifier.
2. **Author**: A model associated with User, containing additional user information such as last activity date, phone number, and last message time.
3. **Content**: A model representing user-generated content, such as articles.
4. **Comment**: A model representing comments on articles.

## Forms:
The project includes the following forms for interacting with the models:

1. **AdminUserCreationForm**: User creation form for administrators
2. **UserSignUpForm**: User registration form
3. **UserLogInForm**: User login form
4. **UserEditForm**: User data editing form
5. **UserPasswordChangeForm**: User password change form
6. **CommentForm**: Form for adding a comment to an article
7. **ContentForm**: Form for creating and editing an article

## Views:
The project uses the following views for handling and displaying requests:

1. **index**, **handler404**: Functional views for basic navigation and error handling.
2. **UserSignUpView**, **UserLogInView**, **UserEditView**: Views for user registration, login, and data editing.
3. **FeedView**, **MyFeedView**: Views for displaying all articles and articles written by a specific user.
4. **ContentView**: View for displaying a specific article and its associated comments.
5. **CreateContentView**, **UpdateContentView**: Views for creating and updating content.

## Templates:
The project utilizes Django templates for rendering content. Most templates are located in the blog/templates/blog directory.

# Installation and Execution
1. Clone the repository: 
```bash
git clone https://github.com/gt-pg1/demo_blog_dj
```
2. Install python-decouple:
```bash
pip install python-decouple
```
3. Copy the .env.example file to .env: 
- **Linux**
```bash
cp .env.example .env
```
- **Windows**
```powershell
copy .env.example .env
```
4. Update the .env file with your environment information (```DB_HOST=localhost``` if you are running the project locally not in Docker)
5. Install PostgreSQL, if not already installed. In Ubuntu, you can use:
- **Linux**
```bash
sudo apt-get install postgresql
```
- **Windows**  
You can download it from [here](https://www.postgresql.org/download/windows/).
6. After installation, create a new database and user for your application. 
- **Linux**
Login to PostgreSQL command line:  
```bash  
sudo -u postgres psql
```
- **Windows**
Open the PostgreSQL command line (pgAdmin tool that comes with PostgreSQL)
7. Create the database:
```sql
CREATE DATABASE your_database_name;
```
8. Create the user:
```sql
CREATE USER your_user WITH PASSWORD 'your_password';
```
9. Grant privileges to the user:
```sql
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_user;
```
10. Exit PostgreSQL command line:
```sql
\q
```

11. Install dependencies: 
```bash
pip install -r requirements.txt
```
12. Apply migrations: 
```
python manage.py migrate
```
13. Start the development server: 
```
python manage.py runserver
```

You can now open the web application in your browser at http://localhost:8000/.

Remember to replace **your_database_name**, **your_user**, and **your_password** with your actual database name, user, and password. Also, remember to update these values in your .env file.

**Important: Do not commit your .env file to the repository. It contains sensitive data. Ensure it is added to your .gitignore file.**

## Installation and Execution using Docker:
If you already have Docker installed, you can use it to install and run the project. Add the Dockerfile and docker-compose.yml files.

**Important: Django Debug Toolbar not showing up when run from Docker container**

Dockerfile:
```bash
    FROM python:3.11
    
    WORKDIR /code
    
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1
    
    RUN pip install --upgrade pip
    COPY ./requirements.txt /code/
    RUN pip install -r requirements.txt
    
    COPY . /code/
```
docker-compose.yml:
```yaml
version: '3.11'

services:
  db:
    image: postgres:13
    volumes:
      - ./data/db:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  web:
    build: .
    command: bash -c "python blogblog/manage.py migrate && python blogblog/manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/code
    ports:
      - 8000:8000
    depends_on:
      - db
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

```
Then you can execute the following commands:

1. Copy the .env.example file to .env: 
- **Linux**
```bash
cp .env.example .env
``` 
- **Windows**
```powershell
copy .env.example .env
``` 
2. Update the .env file with your environment information (```DB_HOST=db``` if you are running the project in Docker)
3. Build the Docker image: 
- **Linux**
```bash
sudo docker-compose build
```
- **Windows**
```powershell
docker-compose build
```
To run the project in the production environment, a separate **docker-compose.prod.yml** file has been created. Accordingly, the command to run in this case will be: 

```bash
docker-compose -f docker-compose.prod.yml build
```
4. Run the Docker container: 
- **Linux**
```bash
sudo docker-compose up
```
- **Windows**
```powershell
docker-compose up
```
You can now open the web application in your browser at http://localhost:8000/.

In production environment:

```bash
docker-compose -f docker-compose.prod.yml up
```

To interact with your Dockerized Django application, you can use ```docker exec``` command. For example, to create a superuser:

```bash
docker exec -it <container_name> python blogblog/manage.py createsuperuser
```

To find out the **container_name**, you can run `docker ps -a`.

## .env file template
The environment variables set all the basic settings for running the project locally or on a web-server.
For comfortable work, modules are used:
- **python-decouple**
- **python-dotenv**

Here is a template for the .env file:

```
SECRET_KEY=<your_secret_key>
DB_NAME=<your_database_name>
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
DB_HOST=<db_or_localhost>
DB_PORT=5432
DJANGO_SETTINGS_MODULE=blogblog.settings.<dev_or_prod>
DJANGO_ALLOWED_HOSTS=127.0.0.1
```
Replace **<your_secret_key>**, **<your_database_name>**, **<your_database_user>**, **<your_database_password>**, **<db_or_localhost>** and **<dev_or_prod>** with your actual data.

To work from a local computer, DJANGO_ALLOWED_HOSTS is enough to leave 127.0.0.1. To place the project on the server, it will need to be replaced with the server IP or domain name.

Note: The value of **<dev_or_prod>** should correspond to the Django settings module you want to use: **blogblog.settings.dev** for development and **blogblog.settings.prod** for production.

The value of **DJANGO_SETTINGS_MODULE** affects the security settings of the project, including the **DEBUG** flag (**DEBUG=True** for development and **DEBUG=False** for production).

Important Security Considerations:
- Be cautious when setting **DEBUG=True** in a production environment. Debug mode can expose sensitive information and is intended for development purposes only.
- Keep your **SECRET_KEY** secure and do not share it publicly. It is used for cryptographic signing and should be kept confidential.
- Ensure that your database credentials (**DB_NAME**, **DB_USER**, **DB_PASSWORD**) are strong and not easily guessable. Limit database access to authorized users only.
- Review and configure the **ALLOWED_HOSTS** setting carefully. In production, specify the appropriate domain names or IP addresses that are allowed to access your application.
- When deploying the application to a production environment, update **DJANGO_SETTINGS_MODULE** to **blogblog.settings.prod** and configure appropriate security measures such as HTTPS, secure server configuration, and access controls.

Make sure to review and update the values in your **.env** file according to your specific project requirements and security guidelines.


# Development
The project was developed using the following technologies and packages:

- Python 3.8
- Django 4.2
- django-debug-toolbar 4.0.0
- django-extensions 3.2.1
- django-tinymce 3.6.1
- psycopg2-binary 2.9.6
- beautifulsoup4 4.12.2
- transliterate 1.10.2
- Unidecode 1.3.6
- and others specified in the requirements.txt file

# License
This project is licensed under the terms of the MIT License.