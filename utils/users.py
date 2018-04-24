# from firebase import firebase
# firebase = firebase.FirebaseApplication('https://shelterme-fe680.firebaseio.com', None)
# firebase not working
from pymongo import MongoClient

server = MongoClient( "127.0.0.1" )

db = server.shelterme

cU = db.users #collection of users
from bson.objectid import ObjectId
targetUser = [{"_key": "1", "email": "Joel", "password": "abc", "userType": "ADMIN"}]

#any potential security code also goes in here
def getUser( userId ):
    """
    users = firebase.get('/users', None)
    targetUser = filter(lambda doc:
                        doc["_key"] == userId, users)
    """
    finder = cU.find_one(
        {"_id": ObjectId(userId) },
    )
    return finder
    
def isValidAccountInfo( email, pwd ):
    """
    users = firebase.get('/users', None)
    targetUser = filter(lambda doc:
                  doc["email"] == email and doc["password"] == pwd, users)
    """
    finder = cU.find_one(
        {"email": email}
    )
    if finder is not None and finder["password"] == pwd:
        return str(finder["_id"])
    return -1
    """
    if len(targetUser) != 0:
        targetUser = targetUser[0]
    else:
        return -1
    """
    return targetUser._id # return session id

def canRegister( email ):
    """
    users = firebase.get('/users', None)
    targetUser = filter(lambda doc:
                        doc["email"] == email, users)
    """
    finder = cU.find_one(
        {"email": email}
    )
    return finder is None
# return len(targetUser) == 0

def registerAccountInfo( email, pwd, userType ):
    """
    users = firebase.get('/users', None)
    targetUser = filter(lambda doc:
                        doc["email"] == email and doc["password"] == pwd, users)
    """
    doc = {}
    doc["email"] = email
    doc["password"] = pwd
    doc["userType"] = userType
    doc["reserve"] = None # Arr [shelterId, seats]
    ret = cU.insert( doc )
    if ret != None:
        return str(ret)

def canReserve(userId):
    u = getUser(userId)
    if u != None:
        if "reserve" in u:
            return u["reserve"] is None
        return True
    return False

# return seats held
def seatsHeld(userId, shelterId):
    u = getUser(userId)
    if u != None:
        if "reserve" in u:
            if u["reserve"] is None:
                return -1
            else:
                if u["reserve"][0] == shelterId:
                    return u["reserve"][1]
                return 0
        else:
            return -1    
    return -1

def reserve(userId, shelterId, amount):
    cU.update_one({'_id': ObjectId(userId)}, {"$set": {"reserve": [shelterId, amount]}}, upsert=False)
    return {"status": "ok", "msg": "Success"} # yep

def cancel(userId):
    user = getUser(userId)    
    cU.update_one({'_id': ObjectId(userId)}, {"$set": {"reserve": None}}, upsert=False)
    return {"status": "ok", "msg": "Success"} # yep

    
