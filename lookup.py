

# Import Libraries
import sqlite3
import json
import xml.etree.ElementTree as ET

try:
    conn = sqlite3.connect("HyperionDev.db")
except sqlite3.Error:
    print("Please store your database as HyperionDev.db")
    quit()

cur = conn.cursor()


def usage_is_incorrect(input, num_args):
    if len(input) != num_args + 1:
        print(f"The {input[0]} command requires {num_args} arguments.")
        return True
    return False


def store_data_as_json(data, filename):  # Store Data as Json
    with open(filename, 'w') as f:
        json.dump(data, f)


def store_data_as_xml(data, filename):  # Store Data as xml
    root = ET.Element("data")
    for item in data:
        child = ET.SubElement(root, "item")
        for index, value in enumerate(item):
            key = f"field_{index}"
            sub_child = ET.SubElement(child, key)
            sub_child.text = str(value)

    tree = ET.ElementTree(root)
    with open(filename, 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)




def offer_to_store(query_result):
    while True:
        print("Would you like to store this result?")
        choice = input("Y/[N]? : ").strip().lower()

        if choice == "y":
            filename = input("Specify filename. Must end in .xml or .json: ")
            ext = filename.split(".")[-1]
            if ext == 'xml':
                store_data_as_xml(query_result, filename)
            elif ext == 'json':
                store_data_as_json(query_result, filename)
            else:
                print("Invalid file extension. Please use .xml or .json")

        elif choice == 'n':
            break

        else:
            print("Invalid choice")



usage = '''
What would you like to do?

d - demo
vs <student_id>            - view subjects taken by a student
la <firstname> <surname>   - lookup address for a given firstname and surname
lr <student_id>            - list reviews for a given student_id
lc <teacher_id>            - list all courses taken by teacher_id
lnc                        - list all students who haven't completed their course
lf                         - list all students who have completed their course and achieved 30 or below
e                          - exit this program

Type your option here: '''

print("Welcome to the data querying app!")

while True:
    print()
    # Get input from user
    user_input = input(usage).split(" ")
    print()

    # Parse user input into command and args
    command = user_input[0]
    if len(user_input) > 1:
        args = user_input[1:]

    if command == 'd':  # demo - a nice bit of code from me to you - this prints all student names and surnames :)
        data = cur.execute("SELECT * FROM Student")
        for _, firstname, surname, _, _ in data:
            print(f"{firstname} {surname}")

    elif command == 'vs':  # view subjects by student_id
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        data = None

        # Run SQL query and store in data

        data = cur.execute(
            "SELECT Course.course_name FROM Course JOIN StudentCourse ON StudentCourse.course_code = Course.course_code JOIN Student ON StudentCourse.student_id = Student.student_id WHERE Student.student_id = ?",
            (student_id,))
        subjects = cur.fetchall()
        print("Subjects for student", student_id, ":")
        for subject in subjects:
            print(subject[0])
        # data = cur.execute("SELECT course_name FROM Courses WHERE teacher_id=?", (teacher_id,))
        # results = cur.fetchall()

        offer_to_store(subjects)


    elif command == 'la':  # list address by name and surname
        if usage_is_incorrect(user_input, 2):
            continue
        firstname, surname = args[0], args[1]
        data = None

        # Run SQL query and store in data
        # . . .
        data = cur.execute(
            "SELECT Address.street, Address.city FROM Address JOIN Student ON Address.address_id = Student.address_id WHERE Student.first_name = ? AND Student.last_name = ?",
            (firstname, surname))
        address = cur.fetchone()
        print("Address for", firstname, surname, ":")
        print(address[0], address[1])

        offer_to_store(address)


    elif command == 'lr':  # list reviews by student_id
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        data = None

        # Run SQL query and store in data
        data = cur.execute(
            "SELECT Review.completeness, Review.efficiency, Review.style, Review.documentation, Review.review_text FROM Review JOIN StudentCourse ON Review.student_id = StudentCourse.student_id AND Review.course_code = StudentCourse.course_code JOIN Student ON StudentCourse.student_id = Student.student_id WHERE Student.student_id = ?",
            (student_id,))
        reviews = cur.fetchall()
        print("Reviews for student", student_id, ":")
        for review in reviews:
            print("Completeness:", review[0])
            print("Efficiency:", review[1])
            print("Style:", review[2])
            print("Documentation:", review[3])
            print("Text:", review[4])

        offer_to_store(reviews)


    elif command == 'lc':  # list all courses taken by teacher_id
        if usage_is_incorrect(user_input, 1):
            continue
        teacher_id = args[0]
        data = None

        # Run SQL query and store in data
        data = cur.execute(
            "SELECT Course.course_name FROM Course JOIN Teacher ON Course.teacher_id = Teacher.teacher_id WHERE Course.teacher_id = ?",
            (teacher_id,))
        courses = cur.fetchall()
        print("Courses taught by teacher", teacher_id, ":")
        for course in courses:
            print(course[0])

        offer_to_store(courses)



    elif command == 'lnc':  # list all students who haven't completed their course
        data = None

        # Run SQL query and store in data
        data = cur.execute(
            "SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name FROM Course JOIN StudentCourse ON StudentCourse.course_code = Course.course_code JOIN Student ON StudentCourse.student_id = Student.student_id WHERE StudentCourse.is_complete = 0")
        incomplete_students = cur.fetchall()
        print("Students who haven't completed their course:")
        for student in incomplete_students:
            print("Student number:", student[0])
            print("Name:", student[1], student[2])
            print("Email:", student[3])
            print("Course name:", student[4])
            print("\n")

        offer_to_store(incomplete_students)


    elif command == 'lf':  # list all students who have completed their course and got a mark <= 30
        data = None

        # Run SQL query and store in data
        data = cur.execute(
            "SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name, StudentCourse.mark FROM Course JOIN StudentCourse ON StudentCourse.course_code = Course.course_code JOIN Student ON StudentCourse.student_id = Student.student_id WHERE StudentCourse.is_complete = 1 AND StudentCourse.mark <= 30")
        poor_students = cur.fetchall()
        print("Students who have completed their course and achieved a mark of 30 or below:")
        for student in poor_students:
            print("Student number:", student[0])
            print("Name:", student[1], student[2])
            print("Email:", student[3])
            print("Course name:", student[4])
            print("Mark:", student[5])
            print("\n")

        offer_to_store(poor_students)


    elif command == 'e':  # list address by name and surname
        print("Programme exited successfully!")
        break

    else:
        print(f"Incorrect command: '{command}'")
