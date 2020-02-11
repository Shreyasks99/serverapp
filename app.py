from flask import Flask, jsonify,request
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
import statement2db as st2db 
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims

)
app = Flask(__name__)
CORS(app)



app.config["MONGO_URI"] = "mongodb://localhost:27017/dhi_analytics"


mongo = PyMongo(app)
# Setup the Flask-JWT-Extended extension


app.config['JWT_SECRET_KEY'] = 'super-secret' 
jwt = JWTManager(app)


class UserObject:
    def __init__(self, username, roles):
        self.username = username
        self.roles = roles


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': user.roles}

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    user = mongo.db.dhi_user.find_one({'email': username})
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    roles = [ x['roleName'] for x in user['roles']]
    user = UserObject(username=user["email"], roles=roles)
    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user,expires_delta=False)
    return jsonify(access_token=access_token), 200

@app.route('/message')
def message():
    return {"message":"Check you luck"}

# Protect a view with jwt_required, which requires a valid access token
# in the request to access.


@app.route('/user', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    ret = {
        'user': get_jwt_identity(),  
        'roles': get_jwt_claims()['roles'] ,
        }
    return jsonify(ret), 200
@app.route('/getAcademicYears')
def getacademicyear():
    year=st2db.getacademicyear()   
    return jsonify({'academicyear':year})

@app.route('/getSemester')
def getSemester():
    sem=st2db.getSemester()
    return jsonify({'semester':sem})

@app.route('/getBranch')
def getBranch():
    branch = st2db.getBranch()
    return jsonify({'branch':branch})



@app.route('/getUsn/<email>')
def getUsn(email):
    usn = st2db.getUsnByEmail(email)
    return jsonify({"usn":usn})

@app.route('/getAttendance/<usn>/<academic>/<term>')
def getAttendance(usn,academic,term):
    attend = st2db.getStudentAttendance(usn,academic,term)
    return jsonify({"res":attend})

@app.route('/getInternal/<usn>/<academic>/<term>')
def getInternal(usn,academic,term):
    internal = st2db.getStudentInternal(usn,academic,term)
    return jsonify({"res":internal})

@app.route('/getCourseAttendance/<course>/<usn>')
def courseAttendance(course,usn):
    attend = st2db.getCourseAttendance(course,usn)
    return jsonify({"res":attend})

@app.route('/getFacultyId/<email>')
def getFacultyid(email):
    eid = st2db.getFacultyId(email)
    return jsonify({"res":eid})

@app.route('/getFacultyAttendance/<eid>/<academic>/<term>')
def getFacultyAttendance(eid,academic,term):
    attend = st2db.getFacultyAttendance(eid,academic,term)
    return jsonify({"res":attend})

@app.route('/getDeptFaculty/<dept>')
def getDeptFaculty(dept):
    faculty = st2db.getDeptFaculty(dept)
    return jsonify({"res":faculty})

@app.route('/getId/<name>')
def getIdByName(name):
    eptid = st2db.getIdByName(name)
    return jsonify({"res":eptid})

@app.route('/getFacultyUE/<eid>/<academic>/<term>')
def getFacultyUE(eid,academic,term):
    UE = st2db.getFacultyUE(eid,academic,term)
    return jsonify({"res":UE})

@app.route('/getFacultyNameByDeptId/<deptId>')
def getFacultyName(deptId):
    name = st2db.getFacultyName(deptId)
    return jsonify({"res":name})

@app.route('/getAttendance/<course>')
def get(course):
    attend = st2db.getAttendance(course)
    return jsonify({"res":attend})

if __name__ == "__main__":
    app.run(port=8088,debug=True)