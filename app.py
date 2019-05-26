import json
import secrets

import requests
from flask import Flask, render_template, request, make_response, session, url_for
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from werkzeug.utils import redirect

from database import db_session
from forms import Itemform
from models import Category, Item

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Get google client_id for this app from json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/logout', methods=["POST"])
def logout():
    session.pop('access_token', None)
    session.pop('user_google_id', None)
    session.pop('username', None)
    session.pop('picture', None)
    session.pop('email', None)
    session.pop('username', None)
    return "Success"


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        state = secrets.token_hex(32)
        session['state'] = state
        return render_template('login.html', STATE=state)
    # try:
    # Check the state variable for extra security
    print("step 0")
    if session['state'] != request.args.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print("step 1")
        return response

    # Retrieve the token sent by the client
    token = request.data
    print("step 2")

    # Request an access tocken from the google api
    idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
    print("step 3")
    url = (
            'https://oauth2.googleapis.com/tokeninfo?id_token=%s'
            % token.decode(encoding='utf-8'))
    # h = httplib2.Http()
    result = requests.get(url).json()
    print("step 4")
    print(result['aud'])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    print("step 5")
    # Verify that the access token is used for the intended user.
    user_google_id = idinfo['sub']
    if result['sub'] != user_google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print(result['sub'])
    # Verify that the access token is valid for this app.
    if result['aud'] != CLIENT_ID:
        print("step 5.5")
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    print("step 6")
    # Check if the user is already logged in
    stored_access_token = session.get('access_token')
    stored_user_google_id = session.get('user_google_id')
    if stored_access_token is not None and user_google_id == stored_user_google_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    print("step 7")
    # Store the access token in the session for later use.
    session['access_token'] = idinfo
    session['user_google_id'] = user_google_id
    # Get user info
    session['username'] = idinfo['name']
    session['picture'] = idinfo['picture']
    session['email'] = idinfo['email']

    return "Successfull"

    # except ValueError:
    #     # Invalid token
    #     print("invalid token")


@app.route("/")
def home():
    items = Item.query.limit(10)
    categories = db_session.query(Category).all()
    return render_template("home.html", categories=categories, items=items)


@app.route("/category/<int:category_id>")
def category_view(category_id):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    items = db_session.query(Item).filter(Item.cat_id == category_id).all()
    return render_template("category.html", category=category, items=items)


@app.route("/category/<int:category_id>/add-item", methods=["GET", "POST"])
def add_item(category_id):
    form = Itemform()
    form.cat_id.choices = [(cat.id, cat.name) for cat in Category.query.all()]
    if form.validate_on_submit():
        item_new = Item(cat_id=form.data.get('cat_id'),
                        description=form.data.get('description'),
                        title=form.data.get('title')
                        )

        db_session.add(item_new)
        db_session.commit()

        return redirect('/category/{}'.format(category_id))
    return render_template("add_item.html", form=form)


@app.route("/category/<int:category_id>/<string:title>")
def item_view(category_id, title):
    item = db_session.query(Item).filter(Item.title == title, Item.cat_id == category_id).first()
    return render_template("item.html", item=item)


@app.route("/category/<int:category_id>/<string:title>/delete", methods=["GET", "POST"])
def item_del(category_id, title):
    item = db_session.query(Item).filter(Item.title == title, Item.cat_id == category_id).first()
    if request.method == "POST":
        if int(request.form.get("del")):
            db_session.delete(item)
            db_session.commit()
            return redirect('/')
        else:
            return redirect('/')
    return render_template("delete.html", item=item)


if __name__ == "__main__":
    # init_db()

    app.debug = True
    app.run(host="0.0.0.0", port=5000, threaded=False)
