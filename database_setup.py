from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    picture = Column(String)

    def __repr__(self):
        return ("<User(name='%s', email='%s', picture='%s')>"
                % (self.name, self.email, self.picture))


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, back_populates='categories')

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


User.categories = relationship("Category", order_by=Category.id,
                               back_populates='user')


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
        }

User.items = relationship("Item", order_by=Item.id,
                          back_populates='user')
Category.items = relationship("Item", order_by=Item.id,
                              back_populates='category')


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
