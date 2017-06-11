# Introduction
This is an application that provides a list of items within a variety of categories as well as a user registration and authentication system. Registered users have teh ability post, edit, and delete their own items.

This project requires Flask 0.12.2, SQLAlchemy 1.1.10, and Python 2.7. Check `requirements.txt` for more details regarding dependencies.

`/templates` contains all HTML templates.
`/static` contains `styles.css`
`main.py` contains the code for the Flask application.

# Installation
Set up Google and Facebook OAuth services, and store the client id and secrets in a JSON file, e.g. `google_client_secrest.json.`

`requirements.txt` is included to note this project's dependencies.

# Operation
Run `database_setup.py` to create the SQLite DB.
Run `populate_catalog.py` to populate the DB with sample data.
Run `main.py` to run the web application.
Open `localhost:5000` in your web browser.

