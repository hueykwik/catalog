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

for category in _CATEGORIES:
    session.add(Category(name=category, user_id=user.id))
session.commit()
