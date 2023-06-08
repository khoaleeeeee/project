"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *
from .common import T, session, auth



def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table('url_mappings',
    Field('url_name',  requires=IS_NOT_EMPTY() ),
    Field('long_url', requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'url_mappings.long_url')]),
    Field('short_id', requires=IS_NOT_EMPTY()),
    Field('user_id', 'reference auth_user', default=lambda: get_user_id()),
    Field('user_email',  default=lambda: get_user_email()),
    Field('created_at', 'datetime', default=get_time),
    auth.signature
)

db.define_table('shared_urls',
    Field('url_mapping_id', 'reference url_mappings'),
    Field('shared_with', 'reference auth_user'),
    Field('shared_by', 'reference auth_user', default=lambda: get_user_id()),
    Field('shared_at', 'datetime', default=get_time),
    auth.signature
)

db.shared_urls.id.readable = db.shared_urls.id.writable = False
db.shared_urls.shared_by.readable = db.shared_urls.shared_by.writable = False
db.shared_urls.shared_at.writable = False

db.url_mappings.id.readable = db.url_mappings.id.writable = False
db.url_mappings.short_id.readable = db.url_mappings.short_id.writable = False
db.url_mappings.user_id.readable = db.url_mappings.user_id.writable = False
db.url_mappings.user_email.readable = db.url_mappings.user_email.writable = False
db.url_mappings.created_at.writable = False

db.commit()
