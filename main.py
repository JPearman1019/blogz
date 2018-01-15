from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app = Flask(__name__)
app.config['DEBUG'] = True

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



@app.route('/', methods=['POST', 'GET'])
def index():    
        
    return render_template('/index.html', title='blog users!')

def not_empty(userinput):
    if userinput != "":
        return True
    return False

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
        blog_id = int(request.args.get('id'))
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('blog.html', title='Build a Blog', blogs=blogs)

    blogs = Blog.query.all()
    return render_template('blog.html', title='blog posts!', blogs=blogs)


@app.route('/blog/newpost', methods=['POST', 'GET'])
def newpost():
    return render_template('newpost.html', title='new post')

@app.route('/add-post', methods=['POST'])
def addpost():
    blog_title = request.form['blog-title']
    blog_entry = request.form['blog-entry']

    title_error = title_val(blog_title)
    body_error = body_val(blog_entry)

    if title_error == "" and body_error == "":
        new_blog = Blog(blog_title, blog_entry)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = str(db.session.query(db.func.max(Blog.id)).scalar())
        
        return redirect('/?id=' + blog_id)

    return render_template('newpost.html', title_error = title_error, body_error = body_error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('signup.html', title='Signup')

@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html', title='Login')

@app.route('/index', methods=['POST', 'GET'])

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    return redirect('/blog')


if __name__ == '__main__':
    app.run()