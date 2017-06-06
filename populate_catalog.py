from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Category, Item, Base

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a dummy user.
user = User(name="Robo Barista", email="tinnyTim@udacity.com",
            picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user)
session.commit()

# Create categories.
_CATEGORIES = ['Soccer',
               'Basketball',
               'Baseball',
               'Frisbee',
               'Snowboarding',
               'Rock Climbing',
               'Foosball',
               'Skating',
               'Hockey']

for category_name in _CATEGORIES:
    category = session.query(Category).filter_by(name=category_name).first()
    if category is None:
        session.add(Category(name=category_name, user_id=user.id))
        session.commit()


def get_category(session, category):
    return session.query(Category).filter_by(name=category).first()

# Use these categories with the items we create below.
soccer = get_category(session, 'Soccer')
baseball = get_category(session, 'Baseball')
frisbee = get_category(session, 'Frisbee')
snowboarding = get_category(session, 'Snowboarding')
hockey = get_category(session, 'Hockey')

# Stick (Hockey)
# Goggles, Snowboard (Snowboarding)
# Two shinguards, Shinguards, Jersey, Soccer Cleats (Soccer)
# Frisbee (Frisbee)
# Bat (Baseball)


def create_item(name, description, category_id, user_id):
    return Item(name=name, description=description, category_id=category_id, user_id=user_id)

session.add(create_item('Stick', 'A hockey stick', hockey.id, user.id))
session.add(create_item('Two Shinguards', 'Two shinguards. Not one.', soccer.id, user.id))
session.add(create_item('Shinguard', 'Just one.', soccer.id, user.id))
session.add(create_item('Jersey', 'My favorite jersey ever.', soccer.id, user.id))
session.add(create_item('Soccer Cleats', 'These are shoes for soccer.', soccer.id, user.id))
session.add(create_item('Frisbee', 'A frisbee. What did you expect?', frisbee.id, user.id))
session.add(create_item('Bat', 'Me my friends and a baseball bat', baseball.id, user.id))
session.commit()


