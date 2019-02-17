from flask import Flask, render_template, request, redirect, url_for, flash
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CatalogItem, User
# new import for sort_query
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import sort_query
# New Import for login
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, jsonify
import requests
threaded = False
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"
app = Flask(__name__)

engine = create_engine('sqlite:///catalogdatabase.db')
engine = create_engine('sqlite:///catalogdatabasewithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
@app.route('/catalog/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# close session if user didn't logout before close out App
@app.route('/clearSession')
def clear_session():
    login_session.clear()
    return "Session cleared"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state paramter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data
    print "session check"
    try:
        # upgradde the authorizatiion code into a credential object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check that the access token is valid
    print "access token check"
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if error in the access token infor, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    print "verify token user"
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's client ID does not match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    print "verify token app"
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match apps's."), 401)
        print "Token's client ID doesn't match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    print "store token"
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    print "get user info"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    print "-==data==-"
    print data
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # see if user exists, if it doesn't make new one
    user_id = getUserID(login_session['email'])
    print "-==user_id==-"
    print user_id
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    print "output"
    output = ''
    output += '<h1>Welcome,'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:\
     150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash ("you are now logged in as %s")   % login_session['username']
    print "done!"
    return output


# helper function for user_id
def createUser(login_session):
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
    session.close()


def getUserInfo(user_id):
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user
    session.close()


def getUserID(email):
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    try:
        # print statements are for degugging
        print "--getUserID--"
        print email
        user = session.query(User).filter_by(email=email).one()
        print user
        session.close()
        return user.id
    except:
        session.close()
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        # print statements are for degugging
        print 'Access Token is None'
        response = make_response(json.dumps
                                 ('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print statements are for degugging
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # return response; print statements are for degugging
        print "sucessfully disconnected"
        print response
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(json.dumps
                                 ('Failed to revoke token for given user.',
                                  400))
        response.headers['Content-Type'] = 'application/json'
        # return response
        return redirect(url_for('showCatalog'))


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # engine = create_engine('sqlite:///catalogdatabase.db')
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sports = session.query(Catalog)
    sports = sort_query(sports, 'category')
    equipments = session.query(CatalogItem)
    equipments = sort_query(equipments, '-item_id')
    session.close()
    if 'username' not in login_session:
        return render_template('publicshowallcatalog.html', sports=sports,
                               equipments=equipments)
    else:
        return render_template('showallcatalog.html', sports=sports,
                               equipments=equipments)


# This route is for user with after login
@app.route('/catalog/add/', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect('/login')
    # engine = create_engine('sqlite:///catalogdatabase.db')
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sports = session.query(Catalog).all()
    equipments = session.query(CatalogItem).all()
    if request.method == 'POST':
        if request.form['New Category'] and request.form['Category']:
            newCategory = Catalog(category=request.form['New Category'],
                                  user_id=login_session['user_id'])
            session.add(newCategory)
            session.commit()
            newEquipment = CatalogItem(title=request.form['Title'],
                                       description=request.form['Desciption'],
                                       category_id=newCategory.id,
                                       user_id=login_session['user_id'])
        # if request.form['Category']:
        elif request.form['Category'] :
            itemCategory = (session.query(Catalog)
                            .filter_by(category=request.form['Category'])
                            .first())
            newEquipment = CatalogItem(title=request.form['Title'],
                                       description=request.form['Desciption'],
                                       category_id=itemCategory.id,
                                       user_id=login_session['user_id'])
        session.add(newEquipment)
        session.commit()
        session.close()
        flash("New Item Created!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html', sports=sports)
    return render_template('newitem.html', sports=sports)


@app.route('/catalog/<string:sport_name>/')
@app.route('/catalog/<string:sport_name>/items/')
def showCatalogItems(sport_name):
    # engine = create_engine('sqlite:///catalogdatabase.db')
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sports = session.query(Catalog).all()
    sport = session.query(Catalog).filter_by(category=sport_name).first()
    countequipment = (session.query(CatalogItem)
                      .filter_by(category_id=sport.id).count())
    equipments = (session.query(CatalogItem)
                  .filter_by(category_id=sport.id).all())
    session.close()
    return render_template('showitem.html', sports=sports, sport=sport,
                           equipments=equipments,
                           countequipment=countequipment)


@app.route('/catalog/<string:sport_name>/<string:goods_name>/')
def showCatalogItemsDescription(sport_name, goods_name):
    # engine = create_engine('sqlite:///catalogdatabase.db')
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sport = session.query(Catalog).filter_by(category=sport_name).first()
    equipments = (session.query(CatalogItem)
                  .filter_by(category_id=sport.id).all())
    equipment = session.query(CatalogItem).filter_by(title=goods_name).first()
    if 'username' not in login_session:
        return render_template('publicitemdescription.html',
                               equipment=equipment, sport=sport)
    else:
        return render_template('itemdescription.html',
                               equipment=equipment, sport=sport)
    session.close()


@app.route('/catalog/<string:sport_name>/<string:goods_name>/edit/',
           methods=['GET', 'POST'])
def editCatalogItems(sport_name, goods_name):
    # engine = create_engine('sqlite:///catalogdatabase.db')
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sports = session.query(Catalog).all()
    sport = session.query(Catalog).filter_by(category=sport_name).first()
    equipments = (session.query(CatalogItem)
                  .filter_by(category_id=sport.id).all())
    equipmentToEdit = (session.query(CatalogItem)
                       .filter_by(title=goods_name).first())
    if 'username' not in login_session:
        return redirect('/login')
    if equipmentToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction() { \
            alert('You are not authorized to edit this item. \
            Please create your own item in order to edit.'); \
            }</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['Title']:
            equipmentToEdit.title = request.form['Title']
            print equipmentToEdit.title
        if request.form['Desciption']:
            equipmentToEdit.description = request.form['Desciption']
        if request.form['Category']:
            itemCategory = (session.query(Catalog)
                            .filter_by(category=request.form['Category'])
                            .one())
            equipmentToEdit.category_id = itemCategory.id
        session.add(equipmentToEdit)
        session.commit()
        session.close()
        flash("Item Edited!")
        return redirect(url_for('showCatalogItemsDescription',
                                sport_name=equipmentToEdit.catalog.category,
                                goods_name=equipmentToEdit.title))
    else:
        return render_template('edititem.html',
                               equipmentToEdit=equipmentToEdit, sports=sports)


@app.route('/catalog/<string:sport_name>/<string:goods_name>/delete/',
           methods=['GET', 'POST'])
def deleteCatalogItems(sport_name, goods_name):
    if 'username' not in login_session:
        return redirect('/login')
    # engine = create_engine('sqlite:///catalogdatabase.db')
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sport = session.query(Catalog).filter_by(category=sport_name).first()
    equipments = (session.query(CatalogItem)
                  .filter_by(category_id=sport.id).all())
    equipmentToDelete = (session.query(CatalogItem)
                         .filter_by(title=goods_name).first())
    if request.method == 'POST':
        session.delete(equipmentToDelete)
        session.commit()
        session.close()
        flash("Catalog Item Deleted!")
        return redirect(url_for('showCatalogItems', sport_name=sport_name))
    else:
        return render_template('deleteitem.html',
                               equipmentToDelete=equipmentToDelete)


# add Json route here
@app.route('/catalog/JSON')
@app.route('/catalog.json')
def showCatalogJSON():
    # engine = create_engine('sqlite:///catalogdatabase.db')
    engine = create_engine('sqlite:///catalogdatabasewithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sports = session.query(Catalog).all()
    equipments = session.query(CatalogItem)
    equipments = sort_query(equipments, '-item_id')
    session.close()
    return jsonify(categoryInCatalog=[i.serialize for i in sports],
                   catalogItem=[j.serialize for j in equipments])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0', port=8000, threaded=False)
