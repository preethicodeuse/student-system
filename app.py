from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        course TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- ADD STUDENT ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO students (name, age, course) VALUES (?, ?, ?)",
            (name, age, course)
        )

        conn.commit()
        conn.close()

        return redirect('/students')

    return render_template('add_student.html')


# ---------------- VIEW + SEARCH ----------------
@app.route('/students', methods=['GET', 'POST'])
def view_students():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        keyword = request.form['keyword']

        query = """
        SELECT * FROM students
        WHERE name LIKE ?
        OR course LIKE ?
        OR age LIKE ?
        """

        value = '%' + keyword + '%'
        cursor.execute(query, (value, value, value))
        students = cursor.fetchall()

    else:
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

    conn.close()

    return render_template('students.html', students=students)


# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/students')


# ---------------- EDIT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        cursor.execute(
            "UPDATE students SET name=?, age=?, course=? WHERE id=?",
            (name, age, course, id)
        )

        conn.commit()
        conn.close()

        return redirect('/students')

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template('edit_student.html', student=student)


# ---------------- EXPORT EXCEL ----------------
@app.route('/export/excel')
def export_excel():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=["ID", "Name", "Age", "Course"])
    file_path = "students.xlsx"
    df.to_excel(file_path, index=False)

    conn.close()

    return send_file(file_path, as_attachment=True)


# ---------------- EXPORT PDF ----------------
@app.route('/export/pdf')
def export_pdf():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()

    file_path = "students.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)

    y = 750
    c.setFont("Helvetica", 12)
    c.drawString(200, 800, "Student Report")

    for s in data:
        text = f"ID:{s[0]}  Name:{s[1]}  Age:{s[2]}  Course:{s[3]}"
        c.drawString(50, y, text)
        y -= 20

        if y < 50:
            c.showPage()
            y = 750

    c.save()

    return send_file(file_path, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
