#
# database.py
#  Bottlerocket database management.
#  
# Created by Martin Bor <m.c.bor@tudelft.nl> on 2012-09-10
# Copyright (c) 2012 TU Delft. All rights reserved.
#

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from bottlerocket import app

engine = create_engine(app.config['DATABASE_URI'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import bottlerocket.models
    Base.metadata.create_all(bind=engine)
