from flask import Flask, flash, render_template, request, session, url_for, redirect
import os, json
from utils import users, shelters

from flask_googlemaps import GoogleMaps, Map

app = Flask(__name__)
app.secret_key = "secrets"

app.config['GOOGLEMAPS_KEY'] = "AIzaSyCt1kRVfq0_DrSBhg9Y3gzRE1ZuGyCd6vw"
GoogleMaps(app)

# ShelterMe
# TODO:
# Login/Logout - Fill out api with firebase
# Link to database
# Build out three pages
# Connect to Maps API

# Site Navigation / Flask Routes =====================

# Home
@app.route("/")
def root():
    message = ""
    if 'message' in request.args:
        message = request.args['message']
    return render_template('index.html', isLoggedIn=isLoggedIn(), message=message)

# Search Shelters / Shelter Results page
@app.route("/search", methods=["GET"])
def search_shelters():
    searchQuery = request.args
    matchingShelters = shelters.findMatchingShelters(searchQuery.to_dict())
    myMap = None
    if len(matchingShelters) != 0:
        myMap = Map(
            identifier="myMap",
            lat="33.780174",
            lng="-84.410142",
            center_on_user_location=True,
            style="height: 300px;width: 450px; margin: auto;",
            markers= map(lambda shelterInfo: {
                    'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                    'lat': shelterInfo["latitude"],
                    'lng': shelterInfo["longitude"],
                    'infobox': """<ul class="list-group">
                    <li class="list-group-item"> Name:""" + shelterInfo["name"]  + """</li>
                    <li class="list-group-item"> Phone:""" + shelterInfo["phone"] + """</li>\
                    </ul>"""
                }, matchingShelters)
            )

    return render_template('search.html', shelterResults=matchingShelters, myMap = myMap)

# Shelter Details page [ Is this a modal ]
@app.route("/shelter/<shelterId>")
def shelter_details(shelterId):
    shelterInfo = shelters.getShelterInfo(shelterId)
    myMap = None
    if shelterInfo != None:
        myMap = Map(
            identifier="myMap",
            lat=shelterInfo["latitude"],
            lng=shelterInfo["longitude"],
            style="height: 300px;width: 450px; margin: auto;",
            markers=[
                {
                    'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                    'lat': shelterInfo["latitude"],
                    'lng': shelterInfo["longitude"],
                    'infobox': """<ul class="list-group">
                    <li class="list-group-item"> Name:""" + shelterInfo["name"]  + """</li>
                    <li class="list-group-item"> Phone:""" + shelterInfo["phone"] + """</li>\
                    </ul>"""
                }
            ]
        )
    if isLoggedIn():
        if users.canReserve(getUser()):
            return render_template('shelter.html', shelter=shelterInfo, canReserve = True, isLoggedIn = True, myMap = myMap)
        seats = users.seatsHeld(getUser(), shelterId) > 0
        if seats > 0:
            return render_template('shelter.html', shelter=shelterInfo, canCancel = True, isLoggedIn = True, myMap = myMap)
        elif seats == 0:
            return render_template('shelter.html', shelter=shelterInfo, committed = True, isLoggedIn = True, myMap = myMap) # already committed
        else:
            return render_template('shelter.html', shelter=shelterInfo, canReserve = True, isLoggedIn = True, myMap = myMap) # shouldn't reach here
    else:
        return render_template('shelter.html', shelter=shelterInfo, myMap = myMap)

@app.route("/reserve/<shelterId>", methods=["POST"])
def reserve(shelterId):
    amount = int(request.form["amount"])
    if isLoggedIn():
        if users.canReserve(getUser()):
            return json.dumps(shelters.reserve(shelterId, getUser(), amount))
        return json.dumps({"status": "error", "msg":"Cannot reserve (You already have a reservation)"})
    return json.dumps({"status": "error", "msg":"User not logged in"})

@app.route("/cancel/<shelterId>", methods=["POST"])
def cancel(shelterId):
    if isLoggedIn():
        seats = users.seatsHeld(getUser(), shelterId)
        if seats > 0:
            return json.dumps(shelters.cancel(shelterId, getUser(), seats))
        return json.dumps({"status": "error", "msg":"Cannot cancel reservation at this shelter (Nothing to cancel)"})
    return json.dumps({"status": "error", "msg":"User not logged in"})


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('root'))

# Login Routes ======================================

@app.route("/login/", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    callbackMessage="Successful login!"
    validate = users.isValidAccountInfo( email, password )
    if validate != -1:
        session['user'] = validate
    else:
        callbackMessage = "Invalid credentials"
    return redirect(url_for('root', message=callbackMessage))

@app.route("/logout/")
def logout():
    callbackMessage = "Logged out"
    if "user" in session:
        session.pop('user')
    else:
        callbackMessage = "Log out request error"
    return redirect(url_for('root', message=callbackMessage))

@app.route("/register/", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]
    userType = request.form["userType"]
    callbackMessage = "Successful register!"
    if users.canRegister(email):
        registerRet = users.registerAccountInfo( email, password, userType )
        if registerRet != None: # -1 for failure
            flash('You successfully registered')
            session['user'] = registerRet
        else:
            callbackMessage="Failed to register (internal error)"
    else:
        callbackMessage = "This email cannot be registered"
    return render_template('index.html', isLoggedIn=isLoggedIn(), message=callbackMessage)
# return redirect( url_for('root', message=callbackMessage) )

# Login Helpers
def isLoggedIn():
    return "user" in session

def getUser():
    if isLoggedIn():
        return session["user"]
    else:
        return None

if __name__ == "__main__":
    app.debug = True
    app.run()
    # app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
    # port = int(os.environ.get('PORT', 5000))
    # socketio.run(app, host = '0.0.0.0', port = port)
