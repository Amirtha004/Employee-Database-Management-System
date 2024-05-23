from flask import Flask, render_template, request, url_for, redirect, jsonify, flash, Response, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = '123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_management'
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/home')
def home():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/view_employees')
def view_employees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    cur.close()
    return render_template('view_employees.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        qualification = request.form['qualification']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        department = request.form['department']

        # Check if email already exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE email = %s", (email,))
        existing_email = cur.fetchone()
        cur.close()

        if existing_email:
            flash('Email already exists', 'error')
            return redirect(url_for('add_employee'))

        # Check if phone number already exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE phone = %s", (phone,))
        existing_phone = cur.fetchone()
        cur.close()

        if existing_phone:
            flash('Phone number already exists', 'error')
            return redirect(url_for('add_employee'))

        # Insert new employee data into the database
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO employees (name, age, qualification, email, phone, position, department) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, age, qualification, email, phone, position, department))
        mysql.connection.commit()
        cur.close()

        flash('Employee added successfully', 'success')
        return redirect(url_for('view_employees'))

    return render_template('add_employee.html')



@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if request.method == 'POST':
        # Process form data and update employee in the database
        name = request.form['name']
        age = request.form['age']
        qualification = request.form['qualification']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        department = request.form['department']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE employees SET name=%s,age=%s,qualification=%s, email=%s, phone=%s, position=%s, department=%s WHERE id=%s", (name,age,qualification, email, phone, position, department, employee_id))
        mysql.connection.commit()
        cur.close()

        flash('Employee updated successfully', 'success')
        return redirect(url_for('view_employees'))
    elif request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
        employee = cur.fetchone()
        cur.close()

        if employee:
            return render_template('edit_employee.html', employee=employee)
        else:
            flash('Employee not found', 'error')
            return redirect(url_for('view_employees'))

@app.route('/delete_employee/<int:employee_id>', methods=['GET', 'POST'])
def delete_employee(employee_id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        mysql.connection.commit()
        cur.close()

        flash('Employee deleted successfully', 'success')
        return redirect(url_for('view_employees'))
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
        employee = cur.fetchone()
        cur.close()

        if employee:
            return render_template('delete_confirmation.html', employee=employee, employee_id=employee_id)
        else:
            flash('Employee not found', 'error')
            return redirect(url_for('view_employees'))


@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        email = request.form['email']  # Change 'username' to 'email'
        password = request.form['password']

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT id, password_set, password FROM employees WHERE email = %s", (email,))
        employee = cursor.fetchone()
        cursor.close()

        if employee:
            employee_id, password_set, stored_password = employee
            if password_set:
                if stored_password == password:
                    return redirect(url_for('employee_view', employee_id=employee_id))
                else:
                    flash('Invalid password. Please try again.', 'error')

            else:
                flash('Password not set. Please set your password.', 'error')
                return redirect(url_for('setup_password'))  # Redirect to password setup page

        else:
            flash('Invalid email. Please try again.', 'error')

    return render_template('employee_login.html')



@app.route('/setup_password', methods=['GET', 'POST'])
def setup_password():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            # Check if the email exists in the database
            cur = mysql.connection.cursor()
            cur.execute("SELECT password_set FROM employees WHERE email = %s", (email,))
            employee = cur.fetchone()

            if employee:
                password_set = employee[0]
                if password_set:
                    flash('Password already set for this email. Please login.', 'info')
                    return redirect(url_for('employee_login'))

                # Store the password in the database and set password_set to True
                cur.execute("UPDATE employees SET password = %s, password_set = True WHERE email = %s", (password, email))
                mysql.connection.commit()
                cur.close()

                flash('Password has been set successfully. Please login.', 'success')
                return redirect(url_for('employee_login'))
            else:
                flash('Email does not exist. Please try again.', 'error')
        else:
            flash('Passwords do not match. Please try again.', 'error')

    return render_template('set_password.html')  # Ensure the cor

@app.route('/employee_view/<int:employee_id>')
def employee_view(employee_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
    employee = cur.fetchone()
    cur.close()

    if employee:
        return render_template('employee_view.html', employee=employee)
    else:
        flash('Employee not found', 'error')
        return redirect(url_for('employee_login'))

@app.route('/edit_user/<int:employee_id>', methods=['GET', 'POST'])
def edit_user(employee_id):
    if request.method == 'POST':
        # Process form data and update employee in the database
        name = request.form['name']
        age = request.form['age']
        qualification = request.form['qualification']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        department = request.form['department']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE employees SET name=%s, age=%s, qualification=%s, email=%s, phone=%s, position=%s, department=%s WHERE id=%s",
                    (name, age, qualification, email, phone, position, department, employee_id))
        mysql.connection.commit()
        cur.close()

        flash('Employee updated successfully', 'success')
        return redirect(url_for('employee_view', employee_id=employee_id))
    elif request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
        employee = cur.fetchone()
        cur.close()

        if employee:
            return render_template('edit_user.html', employee=employee)
        else:
            flash('Employee not found', 'error')
            return redirect(url_for('employee_login'))


@app.route('/employee_logout')
def employee_logout():
    session.pop('employee_id', None)
    return redirect(url_for('employee_login'))



@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)




