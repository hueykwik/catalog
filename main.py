from flask import Flask, render_template
app = Flask(__name__)

_CATEGORIES = ['Soccer',
               'Basketball',
               'Baseball',
               'Frisbee',
               'Snowboarding',
               'Rock Climbing',
               'Foosball',
               'Skating',
               'Hockey']

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


@app.route('/catalog/<string:category>/<string:item>/edit')
def edit_category(category, item):
    return render_template("edit_item.html")


@app.route('/catalog/<string:category>/items')
def show_category(category):
    return render_template("catalog.html", categories=_CATEGORIES,
                           items=_ITEMS, name=category)


@app.route('/')
@app.route('/catalog/')
def catalog():
    return render_template("catalog.html", categories=_CATEGORIES,
                           items=_LATEST, name='Latest')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
