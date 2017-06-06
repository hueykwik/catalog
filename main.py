from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category
from functools import wraps

from flask import Flask, render_template, abort

app = Flask(__name__)

_LATEST = ['Stick',
           'Goggles',
           'Snowboard',
           'Two shinguards',
           'Shinguards',
           'Frisbee',
           'Bat',
           'Jersey',
           'Soccer Cleats']

_ITEMS = ['Goggles', 'Snowboard']

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
    return render_template("catalog.html", categories=categories,
                           items=_ITEMS, name=category)


@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Category).order_by(Category.name).all()
    return render_template("catalog.html", categories=categories,
                           items=_LATEST, name='Latest')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
