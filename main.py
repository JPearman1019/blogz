from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secretkey'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_entry = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_entry, owner):
        self.blog_title = blog_title
        self.blog_entry = blog_entry
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('/index.html', title='blog users!', users=users)

def not_empty(userinput):
    if userinput != "":
        return True
    return False

def len_valid(userinput):
    if len(userinput) >= 3:
        return True
    return False

def str_compare(string1, string2):
    if string1 == string2:
        return True
    return False

def username_val(usernm_input):
    username_error="That's not a valid username"
    if not_empty(usernm_input) and len_valid(usernm_input):
        username_error=""

    return username_error

def password_val(pass_input):
    password_error="That's not a valid password"
    if not_empty(pass_input) and len_valid(pass_input):
        password_error=""

    return password_error

def verify_val(verif_input, pass_input):
    verify_error="Passwords don't match"
    if not_empty(verif_input) and str_compare(verif_input, pass_input):
        verify_error=""

    return verify_error

def title_val(title_input):
    title_empty = "Please fill in the title"
    if not_empty(title_input):
        title_empty=""
    return title_empty

def body_val(body_input):
    body_empty = "Please fill in the body"
    if not_empty(body_input):
        body_empty=""
    return body_empty

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args:
        if request.args.get('id'):
            blog_id = int(request.args.get('id'))
            blogs = Blog.query.filter_by(id=blog_id).all()
            return render_template('blog.html', blogs=blogs)
        else:
            user = request.args.get('user')
            """user_id = User.query.filter_by(username=user).all()"""
            blogs = Blog.query.join(User).filter_by(username=user).all()
            return render_template('blog.html', blogs=blogs)

    blogs = Blog.query.all()
    return render_template('blog.html', title='blog posts!', blogs=blogs)


@app.route('/blog/newpost', methods=['POST', 'GET'])
def newpost():
    return render_template('newpost.html', title='new post')

@app.route('/add-post', methods=['POST'])
def addpost():
    blog_title = request.form['blog-title']
    blog_entry = request.form['blog-entry']
    owner = User.query.filter_by(username=session['username']).first()

    title_error = title_val(blog_title)
    body_error = body_val(blog_entry)

    if title_error == "" and body_error == "":
        new_blog = Blog(blog_title, blog_entry, owner)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = str(db.session.query(db.func.max(Blog.id)).scalar())
        
        return redirect('/blog?id=' + blog_id)

    return render_template('newpost.html', title_error = title_error, body_error = body_error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error=username_val(username)
        password_error=password_val(password)
        verify_error=verify_val(verify, password)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and username_error == "" and password_error == "" and verify_error == "":
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog/newpost')
        elif existing_user:
            return render_template('signup.html', title='Signup', username=username, username_error='A user with that username already exists')
        else:
            return render_template('signup.html', title='Signup', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)    
    return render_template('signup.html', title='Signup')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/blog/newpost')
        else:
            if user and user.password != password:
                return render_template('login.html', title='Login', error='Invalid password')
            return render_template('login.html', title='Login', error='Invalid username')
    return render_template('login.html', title='Login')

@app.route('/index', methods=['POST', 'GET'])

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()