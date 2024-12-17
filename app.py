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


@app.route('/test')
def test():
    return render_template('test.html')  # bynady 3la el html file el fl temp


@app.route('/test2')
def test2():
    x = request.args.get('x')  # gets input from url
    if x is None:
        x = 0

    y = request.args.get('y')
    if y is None:
        y = 0
    name = request.args.get('name')
    x = int(x)  # casted into integer as input from url are interpreted ass string not integer
    y = int(y)
    result = x + y
    return f"result={result},name={name}"


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    input1 = 0
    input2 = 0

    if request.method == 'GET':
        input1 = request.args.get('input1')
        input2 = request.args.get('input2')
    if request.method == 'POST':
        input1 = request.form.get('input1')
        input2 = request.form.get('input2')

    # data validation

    if input1 is None:
        input1 = 0
    if input2 is None:
        input2 = 0

    result = int(input1) * int(input2)
    return render_template('hello.html', r=result)  # bynady 3la el html file el fl temp


@app.route('/')  # This creates a function to connect '/' with home awl ma hayegy / hynady home (kol da fl url)
def home():
    user = session.get('user')  # or  userdata=session['user']
    if user:
        if user['role'] == 'admin':
            cur2 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
            cur2.execute('select * from users')
            records = cur2.fetchall()
            return render_template('index.html', user=user, usersdata=records)

        elif user['role'] == 'patient':
            email = user['email']
            cur2 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
            cur2.execute('SELECT * FROM patients WHERE email = %s ', (email,))
            records = cur2.fetchone()
            return render_template('patient.html', userdata=records)


    else:
        return redirect('/login')


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
    return redirect('/login')


@app.route('/delete/<int:id>')
def delete_user(id):
    cur = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
    cur.execute('SELECT * FROM users WHERE id = %s', (id,))
    records = cur.fetchone()
    email = records['email']

    cur.execute('DELETE FROM allusers WHERE email=%s', (email,))
    cur.execute('DELETE FROM users WHERE id=%s', (id,))


    database_connection_session.commit()
    return redirect('/')


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('AdminAddUser.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    message = request.args.get('message')
    if request.method == 'GET':
        return render_template('EditAdmins.html',aid=id ,msg=message)
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        cur = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)
        cur.execute('SELECT * FROM users WHERE id = %s', (id,))
        records = cur.fetchall()
        oldemail = records['email']
        if records is None:
            message = 'Email does not exist or password is incorrect'
            return redirect(f'/edit/{id}?message={message}')

        if password != confirm_password:
            message = 'Passwords do not match'

        elif oldemail != email:
            # connect to database and store data
            cur2 = database_connection_session.cursor()
            cur2.execute('SELECT * FROM allusers WHERE email = %s', (email,))
            if cur2.fetchone():
                message = 'Email already Exists'
                return redirect(f'/edit/{id}?message={message}')
        else:
            cur1 = database_connection_session.cursor(row_factory=psycopg.rows.dict_row)

            cur1.execute('UPDATE  allusers SET fname=%s , lname =%s , email=%s ,password=%s where oldemail= %s ',
                         (firstname, lastname, email, password, email))  # written this way to make it less hackable
            database_connection_session.commit()
            cur.execute('UPDATE  users SET firstname=%s , lastname =%s , email=%s ,password=%s where oldemail= %s ',
                        (firstname, lastname, email, password, email))
            database_connection_session.commit()
            message = 'Admin Edit Successful'
            return redirect(f'/edit/{id}?message={message}')


if __name__ == '__main__':  ##de heya wl shabaha foo2 ana msh fahemha
    app.run(debug=True)
