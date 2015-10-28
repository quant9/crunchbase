# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = db.create_engine('mysql://root@localhost/crunchbase')
conn = engine.connect()
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def create_tables(engine):
    Base.metadata.create_all(engine)

def now():
    return datetime.datetime.now()


class VCBasics(Base):
    __tablename__ = 'vc_basics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    crunchbase_url = db.Column(db.String(512))
    date_found = db.Column(db.DateTime, default=now)
    run_id = db.Column(db.Integer, index=True)

class VCCategories(Base):
    __tablename__ = 'vc_categories'
    id = db.Column(db.Integer, primary_key=True)
    vc_name = db.Column(db.String(255), db.ForeignKey('vc_basics.name'))
    category = db.Column(db.String(128), index=True)
    category_url = db.Column(db.String(512))
    date_found = db.Column(db.DateTime, default=now)
    run_id = db.Column(db.Integer, index=True)
    __table_args__ = (db.Index('idx_vc_name_category', 'vc_name', 'category', unique=True),)

def store_basics(vc_basics):
    basics = VCBasics(name=vc_basics['name'],
        crunchbase_url=vc_basics['crunchbase_url'],
        run_id=vc_basics['run_id'])
    session.add(basics)
    session.commit()

def store_category(category_dict):
    categories = VCCategories(vc_name=category_dict['vc_name'],
        category=category_dict['category'],
        category_url=category_dict['category_url'],
        run_id=category_dict['run_id'])
    session.add(categories)
    session.commit()
