from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(12000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(15))
    blogs = db.relationship('Post', backref='owner')




    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login_page', 'login_attempt', 'index', 'user_signup', 'verify', 'home']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()

    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def home():
    owner_id = request.args.get('user')
    posts = Post.query.all()
    num_posts = Post.query.count()
    if owner_id is not None:
        owner_id = int(owner_id)
        posts = Post.query.filter_by(owner_id=owner_id)
        num_posts = Post.query.filter_by(owner_id=owner_id).count()
    return render_template('blog.html',title="blogz",
                           posts=posts, num_posts=num_posts)


@app.route('/delete-post', methods = ['POST'])
def delete_post():
    post_id = int(request.form['post-id'])
    post = Post.query.get(post_id)
    post.completed = True

    db.session.add(post)
    db.session.commit()

    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error = ""
    body_error = ""
    #user = session['user']
    #user_id = db.query.filter_by(user).first()
    username = session['username']
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    if request.method == 'POST':

        if request.form['post_title'] == "":
            title_error = "You forgot to give your post a title"
            title = ""
            body = request.form['post_body']
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)
        else:
            post_title = request.form['post_title']

        if request.form['post_body'] == "":
            body = ""
            title = request.form['post_title']
            body_error = "You forgot to give your post a body"
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)
        else:
            post_body = request.form['post_body']
        new_post = Post(post_title, post_body, user_id)
        db.session.add(new_post)
        db.session.commit()
        #added_post = new_post.query.get(new_post)
        #post_id = added_post.id
        post_id = str(new_post.id)
        return redirect('/blog_post?id='+post_id)

    return render_template('newpost.html')


@app.route('/blog_post')
def blog_post():
    post_id = request.args.get('id')
    title = ""
    body = ""
    if post_id is not None:
        post_id = int(post_id)
        result = Post.query.get(post_id)
        title = result.title
        body =  result.body
        username = result.owner.username
        return render_template('blog_post.html', title=title, body=body, username=username, result=result)
    else:
        return render_template('blog_post.html', title=title, body=body)


@app.route("/user_signup", methods=['GET'])
def user_signup():
    username = ""
    username_error = ""
    username = ""
    email = ""
    return render_template('user_signup.html', username="", email="")


@app.route("/user_signup", methods=['POST'])
def verify():
    username_error = ""
    password_error = ""
    verify_error = ""
    email_error = ""

    username = request.form['username']
    password = request.form['password']
    verify_password = request.form['verify_password']
    email = request.form['email']
    taken = User.query.filter_by(username=username).first()

    if username == "":
        username_error = "you must provide a username"
    if taken is not None:
        username_error = "That username has already been registered."
    elif len(username) < 3:
        username_error = "your username isn't long enough, it must be at least three characters long"
    elif len(username) > 20:
        username_error = "your username must be less than 20 characters"

    if password == "":
        password_error = "you must provide a password"
    if len(password) < 3:
        password_error = "your password must be longer than three characters"
    if password != verify_password:
        verify_error = "You password verification was not the same as your password. "

    if verify_password == "":
        verify_error = "you must verify your password"

    if "@" not in email or "." not in email or len(email) > 20 or len(email) < 3 or " " in email:
        email_error = "that is not a valid email"

    if username_error == "" and password_error == "" and verify_error == "" and email_error == "":
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        # added_post = new_post.query.get(new_post)
        # post_id = added_post.id
        #post_id = str(new_post.id)

        session['username'] = username
        return render_template('newpost.html')







    return render_template('user_signup.html', username_error=username_error,
                           password_error=password_error,
                           verify_error=verify_error,
                           email_error=email_error,
                           username=username,
                           email=email
                           )

@app.route("/login", methods=['get'])
def login_page():
    return render_template('login.html', username = "", password = "")

@app.route("/login", methods=['post'])

def login_attempt():

    #Get name and password from form and check to see if they are in the database
    username = request.form['username']
    password = request.form['password']
    username_error = ""
    password_error = ""

    user = User.query.filter_by(username=username).first()

    if user is None or username == "":
        username_error = "That username does not exist."
    else:
        if user.password != password or password == "":
            password_error = "That password is incorrect"

    if username_error == "" and password_error == "":
        session['username'] = username
        return render_template('newpost.html')

    return render_template('login.html', username = "", password = "", username_error=username_error, password_error = password_error)

@app.route("/logout", methods=['get'])
def logout():
    session.pop('username', None)
    return redirect("/login")










if __name__ == '__main__':
    app.run()