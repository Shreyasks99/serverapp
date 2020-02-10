import pymongo
from operator import itemgetter
import re
import bson

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
    result = sorted(res,key=itemgetter("courseName"))
    return result

def getStudentInternal(usn,academic,term):
    collection = db.pms_university_exam
    internal = collection.aggregate([{"$match":{"academicYear":academic}},
    {"$unwind":{'path':"$terms"}},
    {"$match":{"terms.termNumber":term}},
    {"$unwind":{"path":"$terms.scores"}},
    {"$match":{"terms.scores.usn":usn}},
    {"$unwind":{"path":"$terms.scores.courseScores"}},
    {"$group":{"_id":{"coursePerc":"$terms.scores.courseScores.totalScore","usn":"$terms.scores.usn","courseName":"$terms.scores.courseScores.courseName"}}},
    {"$project":{"perc":"$_id.coursePerc","courseName":"$_id.courseName","_id":0}}
    ])
    res = []
    for x in internal:
        res.append(x)
    result = sorted(res,key=itemgetter("courseName"))
    return result

def getCourseAttendance(course,usn):
    collection = db.dhi_student_attendance
    attend = collection.aggregate([
    {"$match":{"courseName":course}},
    {"$unwind":"$students"},
    {"$match":{"students.usn":usn}},
    {"$project":{"total":"$students.totalNumberOfClasses","present":"$students.presentCount","_id":0}}
    ])
    res = []
    for x in attend:
        res.append(x)
    return res[1]

def getFacultyId(email):
    collection = db.dhi_user
    usn = collection.aggregate([{"$match":{"email":email}},{"$project":{"employeeGivenId":1,"_id":0}}])
    res = []
    for x in usn:
        res = x["employeeGivenId"]
    return res

def getFacultyAttendance(eid,academic,term):
    collection = db.dhi_student_attendance
    usn = collection.aggregate([{"$match":{"academicYear":academic,"students.termNumber":term}},
    {"$unwind":{'path':"$faculties"}},
    {"$unwind":{'path':"$faculties.facultyName"}},
    {"$match":{"faculties.employeeGivenId":eid}},
    {"$group":{"_id":{"avg":{"$avg":"$students.percentage"},"faculty":"$faculties.facultyName","course":"$courseName"}}},
    {"$project":{"course":"$_id.course","_id":0,"avg":"$_id.avg"}}
    ])
    res = []
    for x in usn:
        res.append(x)
    result = sorted(res,key=itemgetter("course"))
    return result

def getDeptFaculty(dept):
    collection = db.dhi_user
    pattern = re.compile(f'^{dept}')
    regex = bson.regex.Regex.from_native(pattern)
    regex.flags ^= re.UNICODE 
    faculties = collection.aggregate([
        {"$match":{"roles.roleName":"FACULTY","employeeGivenId":{"$regex":regex}}},
        {"$sort":{"name":1}},
        {"$project":{"employeeGivenId":1,"name":1,"_id":0}}
    ])
    res = []    
    for x in faculties:
        res.append(x)
    return res

def getFacultyUE(eid,academic,term):
    collection =db.dhi_student_attendance
    emp = collection.aggregate([
    {"$match":{"academicYear":academic,"students.termNumber":term}},
    {"$unwind":{'path':"$faculties"}},
    {"$unwind":{'path':"$faculties.facultyName"}},
    {"$match":{"faculties.employeeGivenId":eid}},
    {
    "$lookup":
    {
    "from":"pms_university_exam",
    "localField":"students.usn",
    "foreignField":"terms.scores.usn",
    "as":"usn"
    }
    },
    {"$unwind":{'path':"$usn"}},
    {"$unwind":{'path':"$usn.terms"}},
    {"$unwind":{'path':"$usn.terms.scores"}},
    {"$unwind":{'path':"$usn.terms.scores.courseScores"}},
    {"$match":{"$expr":{"$eq":["$usn.terms.scores.courseScores.courseCode","$courseCode"]}}},
    {"$group":{"_id":{"course":"$courseName"},"ue":{"$push":"$usn.terms.scores.courseScores.ueScore"}}},
    {"$project":{"course":"$_id.course","Avg":{"$avg":"$ue"},"_id":0}}
    ])
    res = []
    for x in emp:
        res.append(x)
    result = sorted(res,key=itemgetter("course"))
    return result








