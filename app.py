from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "studentproject"

# ---------------- LOAD CSV FILES ----------------

users = pd.read_csv("users.csv", dtype=str)
students = pd.read_csv("students.csv")

# Remove extra spaces
users = users.apply(lambda x: x.str.strip() if x.dtype == "object" else x)


# ---------------- CALCULATIONS ----------------

def calculate_average(data):
    data = data.copy()

    data["maths"] = pd.to_numeric(data["maths"])
    data["physics"] = pd.to_numeric(data["physics"])
    data["cs"] = pd.to_numeric(data["cs"])

    data["Average"] = (
        data["maths"] +
        data["physics"] +
        data["cs"]
    ) / 3

    return data


def calculate_risk(data):
    data = data.copy()

    data["attendance"] = pd.to_numeric(data["attendance"])

    data["Risk_Index"] = (
        0.6 * data["Average"] +
        0.4 * data["attendance"]
    )

    return data


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = users[
            (users["username"] == username) &
            (users["password"] == password)
        ]

        if user.empty:
            return render_template(
                "login.html",
                error="Invalid Login"
            )

        user = user.iloc[0]

        session["role"] = user["role"]
        session["department"] = user["department"]
        session["class"] = user["class"]
        session["student_id"] = user["student_id"]

        if user["role"] == "student":
            return redirect(url_for("student_dashboard"))

        elif user["role"] == "teacher":
            return redirect(url_for("teacher_dashboard"))

        elif user["role"] == "hod":
            return redirect(url_for("hod_dashboard"))

        elif user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))

    return render_template("login.html")


# ---------------- STUDENT DASHBOARD ----------------

@app.route("/student")
def student_dashboard():

    if "student_id" not in session:
        return render_template(
            "login.html",
            error="Please log in as a student to access this page."
        )

    sid = session["student_id"]

    data = students[
        students["student_id"] == sid
    ]

    data = calculate_average(data)
    data = calculate_risk(data)

    return render_template("student.html", tables=[data.to_html(classes="table", index=False)])


# ---------------- TEACHER DASHBOARD ----------------

@app.route("/teacher")
def teacher_dashboard():

    if "role" not in session:
        return render_template(
            "login.html",
            error="Please log in as a teacher to access this page."
        )

    dept = session["department"]
    cls = session["class"]

    data = students[
        (students["department"] == dept) &
        (students["class"] == cls)
    ]

    data = calculate_average(data)
    data = calculate_risk(data)

    return render_template("teacher.html",tables=[data.to_html(classes="table", index=False)])


# ---------------- HOD DASHBOARD ----------------

@app.route("/hod")
def hod_dashboard():

    if "role" not in session:
        return render_template(
            "login.html",
            error="Please log in as an HOD to access this page."
        )

    dept = session["department"]

    data = students[
        students["department"] == dept
    ]

    data = calculate_average(data)
    data = calculate_risk(data)

    return render_template("hod.html",tables=[data.to_html(classes="table", index=False)])


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin_dashboard():

    if "role" not in session:
        return render_template("login.html",error="Please log in as an admin to access this page.")

    data = calculate_average(students)
    data = calculate_risk(data)

    return render_template("admin.html",tables=[data.to_html(classes="table", index=False)])


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("login"))


# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)