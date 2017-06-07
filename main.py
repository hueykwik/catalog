from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from functools import wraps

from oauth2client import client, crypt

import random
import string
import json
import httplib2

from flask import Flask, render_template, abort, make_response, request, redirect, url_for
from flask import session as login_session

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

FACEBOOK = 'facebook'
GOOGLE = 'google'
GOOGLE_CLIENT_ID = json.loads(open('google_client_secrets.json', 'r').read())['web']['client_id']


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def login_request_valid(f):
    """Checks that the state parameter from the request matches that of the
    login session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args.get('state') != login_session.get('state'):
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return f(*args, **kwargs)

    return decorated_function


def category_exists(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        category = kwargs['category']
        category = session.query(Category).filter_by(name=category).first()
        if category is None:
            abort(404)
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/logout')
def logout():
    del login_session['provider']
    del login_session['name']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']

    return redirect(url_for('catalog'))


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def createUser(login_session):
    newUser = User(name=login_session['name'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


@app.route('/gconnect', methods=['POST'])
@login_request_valid
def gconnect():
    token = request.form.get('idtoken')

    try:
        idinfo = client.verify_id_token(token, GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

    except crypt.AppIdentityError:
        response = make_response(json.dumps('Wrong issuer.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['provider'] = GOOGLE
    login_session['name'] = idinfo['name']
    login_session['email'] = idinfo['email']
    login_session['picture'] = idinfo['picture']

    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    return "Response"


@app.route('/fbconnect', methods=['POST'])
@login_request_valid
def fbconnect():
    short_lived_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/v2.8/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, short_lived_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    print(data)
    login_session['provider'] = FACEBOOK
    login_session['name'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return "Response"


@app.route('/catalog/<string:category>/<string:item>/delete')
@category_exists
def delete_item(category, item):
    return render_template("delete_item.html")


@app.route('/catalog/<string:category>/new')
@category_exists
def new_item(category):
    return render_template("new_item.html")


@app.route('/catalog/<string:category>/<string:item>/edit')
@category_exists
def edit_item(category, item):
    return render_template("edit_item.html")


@app.route('/catalog/<string:category>/items')
@category_exists
def show_category_items(category):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category).first()
    return render_template("catalog.html", categories=categories,
                           items=category.items, name=category.name)


@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Category).order_by(Category.name).all()
    latest_items = session.query(Item).order_by(Item.id.desc()).all()
    return render_template("catalog.html", categories=categories,
                           items=latest_items, name='Latest')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
