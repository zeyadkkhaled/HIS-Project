from tkinter.constants import CURRENT

from flask import Flask, render_template, request, redirect, session, url_for
import psycopg

app = Flask(__name__)

app.secret_key = 'super secret key'
database_connection_session = psycopg.connect(
    host="ep-square-dew-a59b9xyb.us-east-2.aws.neon.tech",
    dbname="neondb",
    user="neondb_owner",
    password="mO9lIUZN4bDW",
    port=5432
)


@app.route('/')  # This creates a function to connect '/' with home awl ma hayegy / hynady home (kol da fl url)
def home():
    user = session.get('user')  # or  userdata=session['user']
    patient_str = 'patient'
    radiologist_str = 'radiologist'

    if user:

        if user['role'] == 'Admin' or user['role'] == 'admin':
            cur2 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
            cur2.execute('select * from users')
            records1 = cur2.fetchall()
            cur2.execute(
                'SELECT * FROM allusers a INNER JOIN patients p ON a.email = p.email WHERE LOWER(a.role) = %s ',
                (patient_str,))
            records2 = cur2.fetchall()
            cur2.execute(
                'SELECT * FROM allusers a INNER JOIN radiologists r ON a.email = r.email WHERE LOWER(a.role) = %s',
                (radiologist_str,))
            records3 = cur2.fetchall()
            return render_template('index.html', user=user, usersdata=records1, patientsdata=records2,
                                   radiologistsdata=records3)

        elif user['role'] == 'patient' or user['role'] == 'Patient':
            email = user['email']
            cur2 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
            cur2.execute('SELECT * FROM patients WHERE email = %s ', (email,))
            records = cur2.fetchone()
            return render_template('p_profile.html', userdata=records)

        elif user['role'] == 'radiologist' or user['role'] == 'Radiologist':
            email = user['email']
            cur2 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
            cur2.execute('SELECT * FROM radiologists WHERE email = %s', (email,))
            records = cur2.fetchone()
            return render_template('radiologist.html', userdata=records)




    else:
        return redirect('/main')
@app.route('/main')
def main():
 return render_template('main.html')

@app.route('/aboutus')
def aboutus():
 return render_template('aboutus.html')
@app.route('/lmore')
def lmore():
 return render_template('lmore.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = request.args.get('msg')

    if request.method == 'GET':
        return render_template('register.html', msg=message)

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = 'patient'
        sex = request.form.get('sex')

        if password != confirm_password:
            message = 'Passwords do not match'
        else:
            # connect to database and store data
            cur = database_connection_session.cursor()
            cur.execute('SELECT * FROM allusers WHERE email = %s', (email,))
            if cur.fetchone():
                message = 'Email already registered'
            else:
                cur.execute('INSERT INTO patients(firstname, lastname, email,sex) values (%s,%s,%s,%s)',
                            (firstname, lastname, email, sex))  # written this way to make it less hackable
                cur.execute(
                    'INSERT INTO allusers(fname, lname, email, password,role) values (%s,%s,%s,%s,%s)',
                    (firstname, lastname, email, password, role))
                database_connection_session.commit()
                message = 'User registration successful'
                # without commit execution will only be saved temporarily to actually
                # save it in db we should commit

    return redirect(f'/register?msg={message}')


@app.route('/login', methods=['GET',
                              'POST'])  # This creates a function to connect '/' with home awl ma hayegy / hynady home (kol da fl url)
def login():
    message = request.args.get('msg')
    if request.method == 'GET':
        return render_template('login.html', msg=message)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email)
        print(password)
        cur = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
        cur.execute('select * from allusers where email=%s and password=%s', (email, password))
        userdata = cur.fetchone()
        if userdata is None:
            # email or password is incorrect
            message = 'Email does not exist or password is incorrect'
            return redirect(f'/login?msg={message}')
        else:
            session['user'] = userdata
            return redirect('/')


@app.route('/logout')  # This creates a function to connect '/' with home awl ma hayegy / hynady home (kol da fl url)
def logout():
    session.pop('user', None)
    return redirect('/main')


@app.route('/delete/<int:id>/<int:role>')
def delete_user(id, role):
    # if role = 1 means admin , 2 means patient and 3 means radiologist
    cur = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
    if role == 1:
        cur.execute('SELECT * FROM users WHERE id = %s', (id,))
        records = cur.fetchone()
        email = records['email']

        cur.execute('DELETE FROM allusers WHERE email=%s', (email,))
        cur.execute('DELETE FROM users WHERE id=%s', (id,))

        database_connection_session.commit()
    if role == 2:
        cur.execute('SELECT * FROM patients WHERE patientid = %s', (id,))
        records = cur.fetchone()
        email = records['email']

        cur.execute('DELETE FROM allusers WHERE email=%s', (email,))
        cur.execute('DELETE FROM patients WHERE patientid=%s', (id,))

        database_connection_session.commit()
    if role == 3:
        cur.execute('SELECT * FROM radiologists WHERE radiologistid = %s', (id,))
        records = cur.fetchone()
        email = records['email']

        cur.execute('DELETE FROM allusers WHERE email=%s', (email,))
        cur.execute('DELETE FROM radiologists WHERE radiologistid=%s', (id,))

        database_connection_session.commit()
    return redirect('/')


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    message = request.args.get('msg')
    if request.method == 'GET':
        return render_template('AdminAddUser.html', msg=message)
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        sex = request.form.get('sex')
        role = request.form.get('role')
        salary = 0
        cur = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
        cur.execute('SELECT * FROM users where email=%s', (email,))
        records = cur.fetchone()
        if records is None:
            if role == 'admin' or role == 'Admin':
                cur.execute('INSERT INTO users(firstname, lastname, email,password) values (%s,%s,%s,%s)',
                            (firstname, lastname, email, password))  # written this way to make it less hackable
                cur.execute(
                    'INSERT INTO allusers(fname, lname, email, password,role) values (%s,%s,%s,%s,%s)',
                    (firstname, lastname, email, password, role))
                database_connection_session.commit()
                message = 'Admin added successfully'

            elif role == 'patient' or role == 'Patient':
                cur.execute('INSERT INTO patients(firstname, lastname, email,sex) values (%s,%s,%s,%s)',
                            (firstname, lastname, email, sex))  # written this way to make it less hackable
                cur.execute(
                    'INSERT INTO allusers(fname, lname, email, password,role) values (%s,%s,%s,%s,%s)',
                    (firstname, lastname, email, password, role))
                database_connection_session.commit()
                message = 'Patient registration successful'

            elif role == 'technician' or role == 'Technician':
                cur.execute('INSERT INTO technician(firstname, lastname, email,sex,salary) values (%s,%s,%s,%s,%s)',
                            (firstname, lastname, email, sex, salary))  # written this way to make it less hackable
                cur.execute(
                    'INSERT INTO allusers(fname, lname, email, password,role) values (%s,%s,%s,%s,%s)',
                    (firstname, lastname, email, password, role))
                database_connection_session.commit()
                message = 'Technician Added successfully'
            elif role == 'radiologist' or role == 'Radiologist':
                cur.execute('INSERT INTO radiologists(firstname, lastname, email,sex,salary) values (%s,%s,%s,%s,%s)',
                            (firstname, lastname, email, sex, salary))  # written this way to make it less hackable
                cur.execute(
                    'INSERT INTO allusers(fname, lname, email, password,role) values (%s,%s,%s,%s,%s)',
                    (firstname, lastname, email, password, role))
                database_connection_session.commit()
                message = 'Radiologist added successfully'

        else:
            message = 'User Already Exists'
            return redirect(f'/add-user?msg={message}')

    return redirect(f'/add-user?msg={message}')


@app.route('/edit/<int:id>/<int:role>', methods=['GET', 'POST'])
def edit_user(id, role):
    message = request.args.get('message')

    if request.method == 'GET':
        return render_template('EditAdmins.html', id=id, msg=message, role=role)

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        salary = request.form.get('salary')
        CURRENTemail = ''
        records = ''
        cur = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
        if role == 1:
            cur.execute('SELECT * FROM users WHERE id = %s', (id,))
            records = cur.fetchone()

        elif role == 2:
            cur.execute('SELECT * FROM patients WHERE patientid = %s', (id,))
            records = cur.fetchone()

        elif role == 3:
            cur.execute('SELECT * FROM radiologists WHERE radiologistid = %s', (id,))
            records = cur.fetchone()
            if salary is None:
                salary = records['salary']

        CURRENTemail = records['email']
        print(CURRENTemail)
        if password != confirm_password:
            message = 'Passwords do not match'

        if CURRENTemail != email:
            # connect to database and store data
            cur2 = database_connection_session.cursor()
            cur2.execute('SELECT * FROM allusers WHERE email = %s', (email,))
            if cur2.fetchone():
                message = 'Email already Exists'

            else:
                cur1 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)

                cur1.execute('UPDATE  allusers SET fname=%s , lname =%s , email=%s ,password=%s where email= %s ',
                             (firstname, lastname, email, password, CURRENTemail))  # written this way for security
                database_connection_session.commit()
                if role == 1:
                    cur.execute(
                        'UPDATE  users SET firstname=%s , lastname =%s , email=%s ,password=%s where email= %s ',
                        (firstname, lastname, email, password, CURRENTemail))
                    database_connection_session.commit()
                    message = 'Admin Edited Successfully'

                if role == 2:
                    cur.execute('UPDATE  patients SET firstname=%s , lastname =%s , email=%swhere email= %s ',
                                (firstname, lastname, email, CURRENTemail))
                    database_connection_session.commit()
                    message = 'Patient Edited Successfully'
                if role == 3:
                    cur.execute('UPDATE  radiologists SET firstname=%s , lastname =%s , email=%s where email= %s ',
                                (firstname, lastname, email, CURRENTemail))
                    database_connection_session.commit()
                    message = 'Radiologist Edited Successfully'
        if email == CURRENTemail:
            cur1 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)

            cur1.execute('UPDATE  allusers SET fname=%s , lname =%s , email=%s ,password=%s where email= %s ',
                         (firstname, lastname, email, password, CURRENTemail))  # written this way for security
            database_connection_session.commit()
            cur.execute('UPDATE  users SET firstname=%s , lastname =%s , email=%s ,password=%s where email= %s ',
                        (firstname, lastname, email, password, CURRENTemail))
            database_connection_session.commit()
            message = 'Admin Edited Successfully'
            if role == 1:
                cur.execute('UPDATE  users SET firstname=%s , lastname =%s , email=%s ,password=%s where email= %s ',
                            (firstname, lastname, email, password, CURRENTemail))
                database_connection_session.commit()
                message = 'Admin Edited Successfully'

            if role == 2:
                cur.execute('UPDATE  patients SET firstname=%s , lastname =%s , email=%s  where email= %s ',
                            (firstname, lastname, email, CURRENTemail))
                database_connection_session.commit()
                message = 'Patient Edited Successfully'
            if role == 3:
                cur.execute(
                    'UPDATE  radiologists SET firstname=%s , lastname =%s , salary =%s ,email=%s  where email= %s ',
                    (firstname, lastname,salary,email, CURRENTemail))
                database_connection_session.commit()
                message = 'Radiologist Edited Successfully'

    return redirect(f'/edit/{id}/{role}?message={message}')


if __name__ == '__main__':  ##de heya wl shabaha foo2 ana msh fahemha
    app.run(debug=True)
