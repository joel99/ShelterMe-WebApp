# Search related functions
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import BSON
from bson import json_util
import json
import users
server = MongoClient( "127.0.0.1" )

db = server.shelterme

cS = db.shelters #collection of users

# findMatchingShelters - search function (directly accesses db)
def findMatchingShelters(searchQuery):
    allShelters = map(lambda s: {"id": str(s["_id"]), "name": s["name"], "restrictions": s["restrictions"], "phone": s["phone"], "latitude": s["latitude"], "longitude": s["longitude"]}, list(cS.find({}, {"phone": 1, "latitude": 1, "longitude": 1, "name": 1, "restrictions": 1})))
    filtered = allShelters
    if searchQuery != None:
        if "searchName" in searchQuery:
            filterName = searchQuery["searchName"].lower()
            filtered = filter(lambda s: filterName in s["name"].lower(), allShelters)
        filter2 = []
        if "genderChoice" in searchQuery or "ageChoice" in searchQuery:
            for shelter in filtered:
                res = shelter['restrictions']
                if "anyone" in res or len(res) == 0:
                    filter2.append(shelter)
                    continue
                genderFlag = True
                ageFlag = True
                gender = ""
                if 'genderChoice' in searchQuery:
                    gender = searchQuery["genderChoice"].lower()
                age = ""
                if 'ageChoice' in searchQuery:
                    age = searchQuery["ageChoice"].lower()
                    # filter
                if not ('women' in res or 'man' in res):
                    genderFlag = False
                if 'women' in res and gender != 'female':
                    genderFlag = False
                if 'men' in res and gender != 'male':
                    genderFlag = False
                genderFlag = genderFlag or gender == 'unspecified'
                familyFlag = False
                for i in range(len(res)):
                    if "famil" in res[i]:
                        familyFlag = True
                if not (familyFlag or "children" in res or "young adults" in res):
                    ageFlag = False
                if "children" in res and age != "children":
                    ageFlag = False
                if "young adults" in res and age != "young adults":
                    ageFlag = False
                if familyFlag and age != "families with newborns":
                    ageFlag = False
                ageFlag = ageFlag or age == 'unspecified'
                if genderFlag or ageFlag:
                    filter2.append(shelter)
                filtered = filter2
    return filtered

def getShelterInfo(shelterID):
    match = cS.find_one({"_id": ObjectId(shelterID)})
    if match != None:
        match["restrictions"] = ", ".join(match["restrictions"])
    return match

def addFromCSV():
    import csv, numpy as np
    with open('shelters.csv') as File:
        next(File)
        reader = csv.reader(File)
        for row in reader:
            doc = {}
            doc["id"] = row[0]
            doc["name"] = row[1]
            doc["capacity"] = row[2]
            doc["restrictions"] = map(lambda s: s.strip().lower(), row[3].split("/"))
            doc["longitude"] = row[4]
            doc["latitude"] = row[5]
            doc["address"] = row[6]
            doc["notes"] = row[7]
            doc["phone"] = row[8]
            ret = cS.insert(doc)
            if ret == None:
                print "error"

def reserve(shelterId, uId, amount):
    if amount <= 0:
        return {"status": "error", "msg": "Cannot request non-positive space"};
    shelter = cS.find_one({'_id': ObjectId(shelterId)});
    if shelter != None:
        if int(shelter["capacity"]) >= int(amount):
            shelter["capacity"] = int(shelter["capacity"]) - amount
            cS.update_one({'_id': ObjectId(shelterId)}, {"$set": {"capacity": shelter["capacity"]}}, upsert=False) # assume this always works
            userRet = users.reserve(uId, shelterId, amount)
            if userRet["status"] == "ok":
                return {"status": "ok", "msg": "Successful reservation", "delta": -1 * amount}
            else:
                return {"status": "error", "msg": "User reservation failed"} # tbh should undo cS here
        else: # Insufficient capacity
            return {"status": "error", "msg":"Insufficient capacity to reserve"}
    return {"status": "error", "msg": "Reservation error: Internal error"}

def cancel(shelterId, userId, amount):
    shelter = cS.find_one({'_id': ObjectId(shelterId)});
    if shelter != None:
        shelter["capacity"] = int(shelter["capacity"]) + amount
        cS.update_one({'_id': ObjectId(shelterId)}, {"$set": {"capacity": shelter["capacity"]}}, upsert=False)
        users.cancel(userId)
        return {"status": "ok", "msg": "Cancellation success", "delta": amount}
    return {"status": "error", "msg": "Cancellation error: Internal error"}
