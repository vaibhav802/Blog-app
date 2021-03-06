from flask import Flask, render_template, request, flash, redirect, url_for
from flask import abort, session
import pymysql as sql 

app = Flask(__name__)
app.secret_key = b"_!@#$%^kafhdkfj@#$%^&lksdjf!@#$%^"


HOST = 'localhost'
PORT = 3306
USERNAME = 'root'
PASSWORD = ''
DATABASE = 'Blog'



try:
    DB = sql.connect(host=HOST, port=PORT, user=USERNAME, password=PASSWORD, database=DATABASE)
    CURSOR = DB.cursor()
    print("_____________Data Base Connected Sucessfully______________")
except:
    print("_____________Check DATABASE Connectivity First____________________")
    exit(0)

@app.route("/")   
def index():
    if 'username' in session:
        return redirect(url_for('blog'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        abort(405)
    try:
        email = request.form['email']
        password = request.form['password']
        query = f"SELECT * FROM users WHERE email='{email}'"
        rows = CURSOR.execute(query)
        if rows == 0:
            flash("!! No Such Account Exists Please Signup !!")
            return redirect(url_for('signup'))
        else:
            row = CURSOR.fetchone()
            
            upass = row[2]
            if upass == password:
                session['username'] = row[0]
                return redirect(url_for('blog'))
            else:
                flash("!! Error!! Invalid Password Try Again !!")
                return redirect(url_for('index'))
    except:
        flash( "!! Invalid Form Data !!")
        return redirect(url_for('index'))

@app.route("/blog")
def blog():
    return render_template('blog.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route('/do_signup', methods=['POST'])
def do_signup():
    try:
        data = {
        'email': request.form['email'],
        'password': request.form['password'],
        'fname' : request.form['first_name'],
        'lname' : request.form['last_name'],
        'username':  request.form['username'],
        'gender': request.form['sex'],
        'mobile': request.form['ph_no']
        }
    except: 
        data = {'error': 'Invalid Form Data'}
    if 'error' not in data:
        query = f"SELECT * FROM users WHERE email='{data['email']}';"
        rows = CURSOR.execute(query)
        if rows != 0:
            flash("!!! User Account Already Exists Please Login to Continue !!!")
            return redirect(url_for('index'))
        else:
            query = f"SELECT * FROM users WHERE username='{data['username']}'"
            rows = CURSOR.execute(query)
            if rows != 0:
                flash("!! Username Already Taken Please Choose Diffrent Username !!")
                return redirect(url_for('signup'))
            else:
                query = f"INSERT INTO users (username, email, password, first_name, last_name, ph_no, sex) values\
('{data['username']}', '{data['email']}', '{data['password']}', '{data['fname']}', '{data['lname']}',\
 '{data['mobile']}', '{data['gender']}');"
                try:
                    CURSOR.execute(query)
                    DB.commit()
                    flash("!!Account Sucessfully Created Please Login to Enjoy Services!!")
                    return redirect(url_for('index'))
                except:
                    flash("!! Error in Updating Database!!")
                    return redirect(url_for('signup'))
    else:
        flash(data['error'])
        return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data1 = {
        'title': request.form['title'],
        'body':request.form['body'],
        
    }        
        error = None
        
        if not data1['title']:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
    
            CURSOR.execute(
            f"INSERT INTO post (title, body ) VALUES ('{data1['title']}','{data1['body']}');"
            
            )
            DB.commit()

       
            return redirect(url_for('create'))

    return render_template("create.html")

def get_post(id,check_author=True):
    post = CURSOR.execute(
        'SELECT title , body, email'
        ' FROM post '
        ' WHERE email = ?',
        (id,)
    ).fetchone()


    if post is None:
        abort(404, f"Post email {0} doesn't exist.{email}")

    if check_author and post['email'] != id:
        abort(403)

    return post

@app.route('/update', methods=['GET', 'POST'])
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        data2 = {
        'title': request.form['title'],
        'body':request.form['body'],
        
         }        
        error = None
        
    if not data2['title']:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
    
        CURSOR.execute(
        f"INSERT INTO post (title, body ) VALUES ('{data2['title']}','{data2['body']}');"
            
        )
        DB.commit()

       
        return redirect(url_for('create'))

    return render_template("create.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error_msg=error), 404

@app.errorhandler(405)
def page_not_found(error):
    return render_template("error.html", error_msg=error)



app.run(debug=True)



