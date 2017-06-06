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

# soccer, baseball, frisbee, soccer, snowboarding, hockey
soccer = get_category(session, 'Soccer')
baseball = get_category(session, 'Baseball')
frisbee = get_category(session, 'Frisbee')
snowboarding = get_category(session, 'Snowboarding')
hockey = get_category(session, 'Hockey')
