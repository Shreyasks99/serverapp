import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

db=client["dhi_analytics"]



def getacademicyear():
    collection = db.dhi_internal
    academicyear=collection.aggregate([{"$group":{"_id":"null","academicYear":{"$addToSet":"$academicYear"}}},{"$project":{"res":"$academicYear","_id":0}}])
    for year in academicyear:
        year=year['res']
    return year

def getSemester():
    collection = db.dhi_internal
    semester = collection.aggregate([{"$unwind":"$departments"},{"$group":{"_id":"null","sem":{"$addToSet":"$departments.termNumber"}}},{"$project":{"sem":1,"_id":0}}])
    semesters = []
    for s in semester:
        semesters = s["sem"]
    semesters.sort()
    return semesters

def getUsnByEmail(email):
    collection = db.dhi_user
    usn = collection.aggregate([{"$match":{"email":email}},{"$project":{"usn":1,"_id":0}}])
    res = []
    for x in usn:
        res = x["usn"]
    return res

def getStudentAttendance(usn,academic,term):
    collection = db.dhi_student_attendance
    attend = collection.aggregate([{"$match":{"academicYear":academic}},
    {"$unwind":"$students"},
    {"$match":{"students.usn":usn}},
    {"$match":{"students.termNumber":term}},
    {"$group":{"_id":{"perc":"$students.percentage","usn":"$students.usn","course":"$courseName"}}},
    {"$project":{"perc":"$_id.perc","courseName":"$_id.course","_id":0}}
    ])
    res = []
    for x in attend:
        res.append(x)
    return res

def getStudentInternal(usn,academic,term):
    collection = db.pms_university_exam
    internal = collection.aggregate([{"$match":{"academicYear":academic}},
    {"$unwind":{'path':"$terms"}},
    {"$match":{"terms.termNumber":term}},
    {"$unwind":{"path":"$terms.scores"}},
    {"$match":{"terms.scores.usn":usn}},
    {"$unwind":{"path":"$terms.scores.courseScores"}},
    {"$group":{"_id":{"coursePerc":"$terms.scores.courseScores.totalScore","usn":"$terms.scores.usn","courseName":"$terms.scores.courseScores.courseName"}}},
    {"$project":{"perc":"$_id.coursePerc","usn":"$_id.usn","courseName":"$_id.courseName","_id":0}}
    ])
    res = []
    for x in internal:
        res.append(x)
    return res

