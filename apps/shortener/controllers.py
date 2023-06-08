from py4web import action, request, abort, redirect, URL, response
from .common import db, session, T, cache, auth, logger
from .models import get_user_email, get_user_id
import json
from .settings import APP_FOLDER

from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
import hashlib

url_signer = URLSigner(session)

# Shorten a URL using the SHA256 algorithm
# This method has been replaced by another method in shorten() 
# def shorten_url(url):
#     # Generate a hash of the URL using the SHA256 algorithm
#     hash_object = hashlib.sha256(url.encode())
#     hash_str = hash_object.hexdigest()

#     # Take the first 8 characters of the hash as the shortened ID
#     shortened_id = hash_str[:8]

#     # Return the shortened URL with the shortened ID
#     return shortened_id

# Home page
@action('index')
@action.uses('index.html', session, db, auth.user)
def index():
    ### You have to modify the code here as well.
    rows = db(db.url_mappings.user_id == get_user_id()).select()
    return dict(rows=rows, URLSigner=url_signer)

# Shorten a URL
@action('shorten', method=["POST", "GET"])
@action.uses('shorten.html', db, session, auth.user)
def shorten():
    form = Form(db.url_mappings, csrf_session=session, formstyle=FormStyleBulma, dbio=False)
    if form.accepted:
        long_url = form.vars['long_url']
        record = db.url_mappings.insert(
            url_name=form.vars['url_name'], 
            long_url=long_url
        )
        record_id = record.id
        short_id = hex(record_id)[2:]  # Convert the record ID to base 16
        db.url_mappings[record_id] = dict(short_id=short_id)  # Update the record with the short ID
        redirect(URL('index'))
    return dict(form=form)

# Redirect to the original URL given a short ID
@action('redirect/<short_id>')
def redirect_to_long_url(short_id):
    # look up the URL mapping by the short ID
    mapping = db(db.url_mappings.short_id == short_id).select().first()    
    if mapping is None:
        # handle case where short ID is not found in database
        return "Error: Invalid Short URL"
    else:
        # update the click count for the mapping
        # redirect the user's browser to the original URL
        redirect(mapping.long_url)

# Delete a URL
@action('delete/<id:int>')
@action.uses(db, session, auth.user)
def delete(id=None):
    assert(id is not None)
    db(db.url_mappings.id == id).delete()
    redirect(URL('index'))

# Edit a URL
@action('edit/<id:int>', method=["POST", "GET"])
@action.uses( 'edit.html', db, session, auth.user)
def edit(id=None):
    assert(id is not None)
    p = db.url_mappings[id]
    form = Form(db.url_mappings, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

# Get all users to share a URL with
@action("get_users")
@action.uses(db, auth.user)
def get_users():
    query = request.params.get("q", "")
    url_id = request.params.get("url_id")  # Get the url_id parameter

    if query:
        users = db(db.auth_user.username.contains(query)).select()
    else:
        users = db(db.auth_user).select()

    # Get the current user ID
    current_user_id = auth.current_user.get('id')
    # Filter out the current user from the list of users
    users = [user for user in users if user.id != current_user_id]

    # Get the shared_by users for the given url_id
    shared_by_users = db(
        (db.shared_urls.url_mapping_id == url_id)
        & (db.shared_urls.shared_with.belongs([user.id for user in users]))
    ).select(db.shared_urls.shared_with)

    # Add a flag to indicate if each user has shared the URL
    for user in users:
        user.is_shared = any(u.shared_with == user.id for u in shared_by_users)

    return dict(rows=users)

# Share URL page
@action('share/<id:int>')
@action.uses('share.html', session, db, auth.user, url_signer)
def share(id=None):
    assert(id is not None)
    return dict(
        get_users_url = URL('get_users', signer=url_signer),
        send_url = URL('send', signer=url_signer),
        url_id = id
    )

# Send a URL to other users
@action('send', method=["POST"])
@action.uses(db, auth.user, url_signer.verify())
def send():
    url_id = request.json.get('url_id')
    shared_with_json = request.json.get('shared_with')
    shared_with = json.loads(str(shared_with_json)) if shared_with_json else []
    db.shared_urls.insert(url_mapping_id=url_id, shared_with=shared_with)
    return "ok"

# Received URLs page
@action('received')
@action.uses('received.html', session, db, auth.user, url_signer)
def received():
    return dict(
        get_received_url = URL('get_received', signer=url_signer),
    )

# Get all URLs shared with the current user
@action('get_received')
@action.uses(db, auth.user)
def get_received():
    query = request.params.get("q", "")
    if query:
        shared_urls = db(
            (db.shared_urls.shared_with == get_user_id()) & (db.url_mappings.url_name.contains(query))
        ).select(db.shared_urls.url_mapping_id, db.shared_urls.shared_by)
    else:
        shared_urls = db(db.shared_urls.shared_with == get_user_id()).select(db.shared_urls.url_mapping_id, db.shared_urls.shared_by)
    
    url_ids = [row.url_mapping_id for row in shared_urls]
    urls = db(db.url_mappings.id.belongs(url_ids)).select()
    
    received_urls = []
    for url in urls:
        shared_url = next((su for su in shared_urls if su.url_mapping_id == url.id), None)
        if shared_url:
            shared_by = db(db.auth_user.id == shared_url.shared_by).select().first()
            received_urls.append({
                'id': url.id,
                'url_name': url.url_name,
                'long_url': url.long_url,
                'short_id': url.short_id,
                'created_at': url.created_at,
                'shared_by': shared_by,
            })
    return dict(rows=received_urls)



