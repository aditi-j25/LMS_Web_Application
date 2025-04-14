'''=== Group Info ===
Aamna Ghimire (30206981)
Aditi Jain (30208786)

'''

import os
import json
from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# === Paths ===
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
COURSES_PATH = os.path.join(DATA_DIR, "courses.json")
TESTIMONIALS_PATH = os.path.join(DATA_DIR, "testimonials.json")
STUDENTS_PATH = os.path.join(DATA_DIR, "students.json")

# === Load courses and testimonials ===
with open(COURSES_PATH) as f:
    all_courses = json.load(f)

with open(TESTIMONIALS_PATH) as f:
    all_testimonials = json.load(f)

# === Load or initialize students to append to ===
# Note: making a file students.json to show real time appends done by the backend according to interaction with user
if os.path.exists(STUDENTS_PATH):
    with open(STUDENTS_PATH) as f:
        students = json.load(f)
else:
    students = []

# Ensure next_student_id is 1 ahead of current student id
next_student_id = max([s["id"] for s in students], default=0) + 1

# === Save Students to students.json ===
def save_students():
    with open(STUDENTS_PATH, "w") as f:
        json.dump(students, f, indent=2)

# === Getters ===
def get_student_by_username(username):
    return next((s for s in students if s["username"] == username), None)

def get_student_by_id(student_id):
    return next((s for s in students if s["id"] == student_id), None)

# === API ENDPOINTS ===

# === 1) Register API ===
@app.route("/signup", methods=["POST"])
def signup_student():
    global next_student_id #to keep track of the next student id
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data"}), 400 #not json input format
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    existing_student = get_student_by_username(username)
    if existing_student: #if there is a staudent with the same username
        return jsonify({"message": "Username already exists"}), 400
    
    student = { #creating json object for the input for the new student 
        "id": next_student_id,
        "username": username,
        "password": password,
        "email": email,
        "enrolled_courses": []
    }
    students.append(student) #add the new student into the json file 
    next_student_id += 1 #increment 
    save_students() #saves the updated list to the json file 
    return jsonify({"message": "Registered successfully"}), 201

# === 2) Login API ===
@app.route("/login", methods=["POST"])  
def login_student():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data"}), 400
    username = data.get("username")
    password = data.get("password")
    existing_student = get_student_by_username(username)
    if existing_student:
        if existing_student["password"] == password:
            return jsonify({
                "message": "Success", 
                "student_id": existing_student["id"],
             }),200 #print and redirect to the enroll page if the student is found
        else:
            return jsonify({"message": "Invalid password"}), 401
    else:
        return jsonify({"message": "Student not found"}), 404
        

# === 3) Testimonials API ===

@app.route("/testimonials", methods=["GET"])
def get_testimonials():
    return jsonify(random.sample(all_testimonials, 2)), 200

# === 4) Enroll Courses API === 

@app.route("/enroll/<int:student_id>", methods=["POST"])
def enroll_course(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    course = request.get_json()
    already_enrolled = any(c["id"] == course["id"] for c in student["enrolled_courses"])
    if already_enrolled:
        return jsonify({"message": "Already enrolled"}), 400

    course["enrollmentId"] = f"{student_id}-{course['id']}"
    student["enrolled_courses"].append(course)
    save_students()
    return jsonify({"message": "Enrolled successfully"}), 200


# === 5) Enroll Courses API === 

@app.route("/drop/<int:student_id>", methods=["DELETE"])
def drop_course(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    data = request.get_json()
    enrollment_id = data.get("enrollmentId")

    before = len(student["enrolled_courses"])
    student["enrolled_courses"] = [
        c for c in student["enrolled_courses"] if c.get("enrollmentId") != enrollment_id
    ]
    after = len(student["enrolled_courses"])

    if before == after:
        return jsonify({"message": "Enrollment not found"}), 404

    save_students()
    return jsonify({"message": "Course dropped"}), 200

# === 6) Get All Courses API === 
@app.route("/courses", methods=["GET"])
def get_courses():
    return jsonify(all_courses), 200


# === 7) Get Student Courses API === 
@app.route("/student_courses/<int:student_id>", methods=["GET"])
def get_student_courses(student_id):
    student = get_student_by_id(student_id)
    return jsonify(student["enrolled_courses"] if student else []), 200


if __name__ == "__main__":
    app.run(debug=True)
