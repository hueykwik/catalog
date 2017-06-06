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


@app.route('/')
@app.route('/catalog/')
def catalog():
    return render_template("catalog.html")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
