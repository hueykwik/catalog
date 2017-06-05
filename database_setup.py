from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite:///catalog.db')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    picture = Column(String)

    def __repr__(self):
        return "<User(name='%s', email='%s', picture='%s')>" % (self.name, self.email, self.picture)

Base.metadata.create_all(engine)
