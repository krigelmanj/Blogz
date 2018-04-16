from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Post(db.Model):

    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(12000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def home():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def index():



    posts = Post.query.all()

    return render_template('blog.html',title="Build-a-blog",
                           posts=posts)


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
        new_post = Post(post_title, post_body)
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
        return render_template('blog_post.html', title=title, body=body)
    else:
        return render_template('blog_post.html', title=title, body=body)

if __name__ == '__main__':
    app.run()