from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgresql://udacity:udacity@localhost/udacity')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)

    cat1 = models.Category('DOm')
    cat2 = models.Category('kot')
    cat3 = models.Category('pies')

    db_session.add(cat1)
    db_session.add(cat2)
    db_session.add(cat3)

    db_session.commit()
