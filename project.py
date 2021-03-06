import json
import random
import string

import httplib2
import requests
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as login_session
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

# from database_setup import Base, Restaurant, MenuItem


app = Flask(__name__)
# Get google client_id for this app from json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
# engine = create_engine('sqlite:///restaurantmenu.db')
# Base.metadata.bind = engine
#
# DBSession = sessionmaker(bind=engine)
# session = DBSession()


@app.route('/login', methods=['GET', 'POST'])
def showLogin():
    if request.method == 'GET':
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        login_session['state'] = state
        return render_template('login_html.html', STATE=state)
    if request.method == 'POST':
        try:
            # Check the state variable for extra security
            print("step 0")
            if login_session['state'] != request.args.get('state'):
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
                print
                "Token's client ID does not match app's."
                response.headers['Content-Type'] = 'application/json'
                return response
            print("step 6")
            # Check if the user is already logged in
            stored_access_token = login_session.get('access_token')
            stored_user_google_id = login_session.get('user_google_id')
            if stored_access_token is not None and user_google_id == stored_user_google_id:
                response = make_response(
                    json.dumps('Current user is already connected.'), 200)
                response.headers['Content-Type'] = 'application/json'
                return response
            print("step 7")
            # Store the access token in the session for later use.
            login_session['access_token'] = idinfo
            login_session['user_google_id'] = user_google_id
            # Get user info
            login_session['username'] = idinfo['name']
            login_session['picture'] = idinfo['picture']
            login_session['email'] = idinfo['email']

            return 'Successful'


        except ValueError:
            # Invalid token
            pass
#
#
# @app.route('/welcome')
# def welcome():
#     return render_template('welcome.html', picture=login_session['picture'], fullname=login_session['username'])
#
#
# # JSON APIs to view Restaurant Information
# @app.route('/restaurant/<int:restaurant_id>/menu/JSON')
# def restaurantMenuJSON(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
#     return jsonify(MenuItems=[i.serialize for i in items])
#
#
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
# def menuItemJSON(restaurant_id, menu_id):
#     Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
#     return jsonify(Menu_Item=Menu_Item.serialize)
#
#
# @app.route('/restaurant/JSON')
# def restaurantsJSON():
#     restaurants = session.query(Restaurant).all()
#     return jsonify(restaurants=[r.serialize for r in restaurants])
#
#
# # Show all restaurants
# @app.route('/')
# @app.route('/restaurant/')
# def showRestaurants():
#     restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
#     return render_template('restaurants.html', restaurants=restaurants)
#
#
# # Create a new restaurant
# @app.route('/restaurant/new/', methods=['GET', 'POST'])
# def newRestaurant():
#     if request.method == 'POST':
#         newRestaurant = Restaurant(name=request.form['name'])
#         session.add(newRestaurant)
#         flash('New Restaurant %s Successfully Created' % newRestaurant.name)
#         session.commit()
#         return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('newRestaurant.html')
#
#
# # Edit a restaurant
# @app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
# def editRestaurant(restaurant_id):
#     editedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedRestaurant.name = request.form['name']
#             flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
#             return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('editRestaurant.html', restaurant=editedRestaurant)
#
#
# # Delete a restaurant
# @app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
# def deleteRestaurant(restaurant_id):
#     restaurantToDelete = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         session.delete(restaurantToDelete)
#         flash('%s Successfully Deleted' % restaurantToDelete.name)
#         session.commit()
#         return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
#     else:
#         return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)
#
#
# # Show a restaurant menu
# @app.route('/restaurant/<int:restaurant_id>/')
# @app.route('/restaurant/<int:restaurant_id>/menu/')
# def showMenu(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
#     return render_template('menu.html', items=items, restaurant=restaurant)
#
#
# # Create a new menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
# def newMenuItem(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         newItem = MenuItem(name=request.form['name'], description=request.form['description'],
#                            price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
#         session.add(newItem)
#         session.commit()
#         flash('New Menu %s Item Successfully Created' % (newItem.name))
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('newmenuitem.html', restaurant_id=restaurant_id)
#
#
# # Edit a menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
# def editMenuItem(restaurant_id, menu_id):
#     editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedItem.name = request.form['name']
#         if request.form['description']:
#             editedItem.description = request.form['description']
#         if request.form['price']:
#             editedItem.price = request.form['price']
#         if request.form['course']:
#             editedItem.course = request.form['course']
#         session.add(editedItem)
#         session.commit()
#         flash('Menu Item Successfully Edited')
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)
#
#
# # Delete a menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
# def deleteMenuItem(restaurant_id, menu_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
#     if request.method == 'POST':
#         session.delete(itemToDelete)
#         session.commit()
#         flash('Menu Item Successfully Deleted')
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('deleteMenuItem.html', item=itemToDelete)
#


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
