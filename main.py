from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from functools import wraps

from oauth2client import client

import random
import string
import json
import httplib2
import requests

from flask import Flask, render_template, abort
from flask import make_response, request, redirect, url_for, jsonify
from flask import session as login_session

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

FACEBOOK = 'facebook'
GOOGLE = 'google'
GOOGLE_CLIENT_ID = json.loads(open('google_client_secrets.json',
                                   'r').read())['web']['client_id']


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('show_login'))
        return f(*args, **kwargs)
    return decorated_function


def item_owner(f):
    """Decorator that checks that the logged in user is the owner of
    the item name being requested.

    The decorator queries the DB for a matching Item. If found, it sets
    `item` to the matching Item and calls the inner function. If not found,
    it returns an error message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        item = kwargs['item']
        item = session.query(Item).filter_by(name=item).first()
        if item.user_id != login_session.get('user_id'):
            response_text = json.dumps('Not allowed to edit/delete this item.')
            response = make_response(response_text, 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            kwargs['item'] = item
            return f(*args, **kwargs)

    return decorated_function


def login_request_valid(f):
    """Checks that the state parameter from the request matches that of the
    login session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args.get('state') != login_session.get('state'):
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return f(*args, **kwargs)

    return decorated_function


def category_exists(f):
    """Checks that the category name being requested exists.
    """
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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


def gdisconnect():
    access_token = login_session.get('access_token')
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        print("Couldn't revoke token for user")


@app.route('/logout')
def logout():
    print('in logout')
    if login_session['provider'] == GOOGLE:
        gdisconnect()
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
    """
    Uses the Google One Time Code flow sign-in to log in the user.
    """
    auth_code = request.data

    # If this request does not have `X-Requested-With` header,
    # this could be a CSRF.
    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Exchange one time code for access token.
    CLIENT_SECRET_FILE = 'google_client_secrets.json'
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
        auth_code)

    # Use access token to get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = GOOGLE
    login_session['access_token'] = credentials.access_token
    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

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

    url = "https://graph.facebook.com/v2.8/oauth/access_token?" \
          "grant_type=fb_exchange_token&client_id=%s" \
          "&client_secret=%s&fb_exchange_token=%s"
    url = url % (app_id, app_secret, short_lived_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print(data)
    login_session['provider'] = FACEBOOK
    login_session['name'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order
    # to properly logout, let's strip out the information
    # before the equals sign in our token.
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = "https://graph.facebook.com/v2.4/me/picture" \
          "?%s&redirect=0&height=200&width=200" % token
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


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s'
           % (facebook_id, access_token))
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/catalog/<string:category>/<string:item>/delete',
           methods=['GET', 'POST'])
@login_required
@category_exists
@item_owner
def delete_item(category, item):
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template("delete_item.html")


@app.route('/catalog/new', methods=['GET', 'POST'])
@login_required
def new_item():
    if request.method == 'POST':
        name = request.form['category']
        category = session.query(Category).filter_by(name=name).first()
        new_item = Item(name=request.form['name'],
                        description=request.form['description'],
                        user_id=login_session['user_id'],
                        category_id=category.id)
        session.add(new_item)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        categories = session.query(Category).all()
        return render_template("new_item.html", categories=categories)


@app.route('/catalog/<string:category>/<string:item>/edit',
           methods=['GET', 'POST'])
@login_required
@category_exists
@item_owner
def edit_item(category, item):
    if request.method == 'POST':
        name = request.form['category']
        category = session.query(Category).filter_by(name=name).first()
        item.name = request.form['name']
        item.description = request.form['description']
        item.category_id = category.id
        session.add(item)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        categories = session.query(Category).all()

        return render_template("edit_item.html", categories=categories,
                               name=item.name, description=item.description,
                               selected=category)


@app.route('/catalog/<string:category>/<string:item>/JSON')
def show_item_json(category, item):
    item = session.query(Item).filter_by(name=item).one()
    return jsonify(item=item.serialize)


@app.route('/catalog/<string:category>/<string:item>')
def view_item(category, item):
    item = session.query(Item).filter_by(name=item).one()
    can_edit = (item.user_id == login_session.get('user_id'))

    return render_template("view_item.html", item=item, can_edit=can_edit)


@app.route('/catalog/<string:category>/items')
@category_exists
def show_category_items(category):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category).first()
    return render_template("catalog.html", categories=categories,
                           items=category.items, name=category.name)


@app.route('/catalog/JSON')
def show_catalog_json():
    categories = session.query(Category).all()

    category_data = []
    for category in categories:
        data = category.serialize
        items = session.query(Item).filter_by(id=category.id).all()
        items_data = [item.serialize for item in items]
        data['Item'] = items_data

        category_data.append(data)

    return jsonify(categories=category_data)


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
