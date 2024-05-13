from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import sqlite3

app = Flask(__name__)
api = Api(app, version='1.0', title='Student API',
          description='A simple Student API',
          doc='/docs')

# Namespace
ns = api.namespace('students', description='Operations related to students')


app.config['ERROR_404_HELP'] = False
# Database connection function
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('students.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn

# Model definition
student_model = api.model('Student', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a student'),
    'firstname': fields.String(required=True, description='First name of the student'),
    'lastname': fields.String(required=True, description='Last name of the student'),
    'gender': fields.String(required=True, description='Gender of the student'),
    'age': fields.Integer(required=True, description='Age of the student')
})

# Students collection operations
@ns.route('/')
class StudentList(Resource):
    @ns.doc('list_students')
    @ns.marshal_list_with(student_model)
    def get(self):
        """List all students"""
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        return jsonify(students)

    @ns.doc('create_student')
    @ns.expect(student_model)
    @ns.marshal_with(student_model, code=201)
    def post(self):
        """Create a new student"""
        conn = db_connection()
        cursor = conn.cursor()
        student = request.form
        sql = """INSERT INTO students (firstname, lastname, gender, age)
                 VALUES (?, ?, ?, ?)"""
        cursor.execute(sql, (student['firstname'], student['lastname'], student['gender'], student['age']))
        conn.commit()
        return jsonify(student), 201

# Single student operations
@ns.route("/<int:id>")
@ns.response(404, 'Student not found')
@ns.param('id', 'The student identifier')
class Student(Resource):
    @ns.doc('get_student')
    @ns.marshal_with(student_model)
    def get(self, id):
        """Fetch a student given its identifier"""
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id=?", (id,))
        student = cursor.fetchone()
        if student:
            return jsonify(student)
        api.abort(404, "Student not found")

    @ns.doc('delete_student')
    @ns.response(204, 'Student deleted')
    def delete(self, id):
        """Delete a student given its identifier"""
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id=?", (id,))
        conn.commit()
        return '', 204

    @ns.expect(student_model)
    @ns.marshal_with(student_model)
    def put(self, id):
        """Update a student given its identifier"""
        student = request.form
        conn = db_connection()
        cursor = conn.cursor()
        sql = """UPDATE students SET firstname=?, lastname=?, gender=?, age=? WHERE id=?"""
        cursor.execute(sql, (student['firstname'], student['lastname'], student['gender'], student['age'], id))
        conn.commit()
        return jsonify(student)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
