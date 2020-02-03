import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db=client["dhi_analytics"]



def getacademicyear():
    collection = db.dhi_internal
    academicyear=collection.aggregate([{"$group":{"_id":"null","academicYear":{"$addToSet":"$academicYear"}}},{"$project":{"res":"$academicYear","_id":0}}])
    for year in academicyear:
        year=year['res']
    return year
