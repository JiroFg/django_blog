# Django Blog App

This aplication was created with django, you can see all the blog posts and add new ones, as well as share the posts by email.
This project was build with python 3.12

To run this project just follow these steps:

1. Create a new virtual enviroment(In my case with conda):
> `conda create -n 'blog_venv' python=3.12`

2. Activate the virtual enviroment:
> `conda activate blog_venv`

3. Install the dependencies:
> `pip install -r requirements.txt`

4. Create you .env file from example.env file and replace the variables

5. Make the migrations file:
> `python manage.py makemigrations`

6. Apply the migrations:
> `python manage.py migrate`

7. Finally run the server:
> `python manage.py runserver`

Developed by JiroFg

docker run --name=blog_db -e POSTGRES_DB=blog -e POSTGRES_USER=blog -e POSTGRES_PASSWORD=Secret125 -p 5432:5432 -d postgres:16.2  