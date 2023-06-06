from py4web import action, request, abort, redirect, URL, response
from .common import db, session, T, cache, auth, logger
from .models import get_user_email, get_user_id
import json
from .settings import APP_FOLDER

from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
import hashlib

url_signer = URLSigner(session)

def shorten_url(url):
    # Generate a hash of the URL using the SHA256 algorithm
    hash_object = hashlib.sha256(url.encode())
    hash_str = hash_object.hexdigest()

    # Take the first 8 characters of the hash as the shortened ID
    shortened_id = hash_str[:8]

    # Return the shortened URL with the shortened ID
    return shortened_id

@action('index')
@action.uses('index.html', session, db, auth.user)
def index():
    ### You have to modify the code here as well.
    rows = db(db.url_mappings.user_id == get_user_id()).select()
    return dict(rows=rows, URLSigner=url_signer)

#TODO: check check valid URL, check if URL already exists
@action('shorten', method=["POST", "GET"])
@action.uses(db, session, auth.user, 'shorten.html')
def shorten():
    form = Form(db.url_mappings, csrf_session=session, formstyle=FormStyleBulma, dbio=False)
    if form.accepted:
        long_url = form.vars['long_url'] 
        db.url_mappings.insert(
            url_name=form.vars['url_name'], 
            long_url=long_url, 
            short_id=shorten_url(long_url))
        redirect(URL('index'))
    return dict(form=form)


@action('redirect/<short_id>')
def redirect_to_long_url(short_id):
    # look up the URL mapping by the short ID
    mapping = db(db.url_mappings.short_id == short_id).select().first()
    print(mapping.long_url)
    if mapping is None:
        # handle case where short ID is not found in database
        return "Error: Invalid Short URL"
    else:
        # update the click count for the mapping
        # redirect the user's browser to the original URL
        redirect(mapping.long_url)

#TODO: add delete button
@action('delete/<id:int>')
@action.uses(db, session, auth.user)
def delete(id=None):
    assert(id is not None)
    db(db.url_mappings.id == id).delete()
    db.commit()
    redirect(URL('index'))

#TODO: add edit button
@action('edit/<id:int>', method=["POST", "GET"])
@action.uses(db, session, auth.user, 'edit.html')
def edit(id=None):
    assert(id is not None)
    p = db.url_mappings[id]
    form = Form(db.url_mappings, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma, dbio=False)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action("get_users")
@action.uses(db, auth.user)
def get_users():
    query = request.params.get("q", "")
    if query:
        users = db(db.auth_user.username.contains(query)).select()
    else:
        users = db(db.auth_user).select()

    # Get the current user ID
    current_user_id = auth.current_user.get('id')
    # Filter out the current user from the list of users
    users = [user for user in users if user.id != current_user_id]

    return dict(rows=users)


@action('share/<id:int>')
@action.uses('share.html', session, db, auth.user, url_signer)
def share(id=None):
    assert(id is not None)
    return dict(
        get_users_url = URL('get_users', signer=url_signer),
        send_url = URL('send', signer=url_signer),
        url_id = id
    )

@action('send', method=["POST"])
@action.uses(db, auth.user, url_signer.verify())
def send():
    print(request.json)
    url_id = request.json.get('url_id')
    shared_with_json = request.json.get('shared_with')
    shared_with = json.loads(str(shared_with_json)) if shared_with_json else []
    db.shared_urls.insert(url_mapping_id=url_id, shared_with=shared_with)
    db.commit()
    return "ok"