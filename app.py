from flask import Flask,redirect,request,render_template,flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mine.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.secret_key = "334455"

UPLOAD_FOLDER = "./static/imgs"
ALLOWED_EXTENSION = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER

class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow())

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    image = db.Column(db.String(200),nullable=False)
    content = db.Column(db.String(200),nullable=False)
    cat_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime,default=datetime.utcnow())

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(200),nullable=False)
    password = db.Column(db.String(200),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow())

@app.route('/logout')
def logout():
    session['username']=""
    session['email']    =""
    return redirect('/login')

@app.route('/login',methods = ['POST','GET'])
def login():
    context = {
         "title":"Login page"
    }
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password,password):
                flash("Welcome back")
                session["username"] = user.name
                session["email"] = user.email
                return redirect('/')
            else:
                return redirect('/login')
        else:
            return redirect('/login')

    else:
        return render_template('login.html',context=context)


@app.route('/register',methods=['POST','GET'])
def register():
    context = {
         "title":"Register page"
    }
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password = bcrypt.generate_password_hash(password)
        user = User(name=name,email=email,password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            return render_template('register.html',context=context)
    else:
        return render_template('register.html',context=context)

@app.route('/')
def catHome():
    cats = Category.query.all()
    context = {
        "title":"Cat Home page",
        "cats":cats

    }
    return render_template('cat_home.html',context=context)

@app.route('/cats/create',methods=['POST','GET'])
def catCreate():
    context = {
        "title":"Cat Home page"
    }
    if request.method=='POST':
        name = request.form['name']
        cats = Category(name=name)
        try:
            db.session.add(cats)
            db.session.commit()
            return redirect('/')
        except:
            return render_template('cat_create.html',context=context)
    else:
        return render_template('cat_create.html',context=context)
    

@app.route('/cats/edit/<int:id>',methods=['GET','POST'])
def catEdit(id):
    cats = Category.query.get_or_404(id)
    context = {
        "title":"Cat Home page",
        "cats":cats
    }
    if request.method == 'POST':
        name = request.form['name']
        cats.name=name
        try:
            db.session.commit()
            return redirect('/')
        except:
            return render_template('cat_edit.html',context=context)
    else:
        return render_template('cat_edit.html',context=context)

@app.route('/cats/delete/<int:id>')
def catDelete(id):
    cats = Category.query.get_or_404(id)
    db.session.delete(cats)
    db.session.commit()
    return redirect('/')


@app.route('/post/edit/<int:id>',methods=['POST','GET'])
def postEdit(id):
    posts = Post.query.get_or_404(id)
    context = {
        "title":"Post Edit page",
        "cats" : Category.query.all(),
        "posts": posts
    }
    if request.method=='POST':
        filename = ''
        file = request.files['image']
    
        if file.filename =='':
            return redirect('/post/edit')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        title = request.form['title']
        cat_id = request.form['catid']
        content = request.form['content']
        posts = Post(title=title,content=content,cat_id=cat_id, image=filename)
        try:
            db.session.commit()  #  if success
            return redirect('/post')
        except:
            return redirect('post/edit')
    else:
        return render_template('post_edit.html',context=context)

@app.route('/post')
def postHome():
    
    
    context = {
        "posts":Post.query.all(),
        "title":"Post Home page",
        "cats" : Category.query.all()
    }
    return render_template('post.html',context=context)

@app.route('/post/create',methods=['POST','GET'])
def postCreate():
    context = {
        "title":"Post Create page",
        "cats" : Category.query.all()
    }
    if request.method=='POST':
        filename = ''
        file = request.files['image']
    
        if file.filename =='':
            return redirect('/post/create')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        cat_id = request.form["catid"]
        title = request.form["title"]
        content = request.form["content"]
        post = Post(title=title,content=content,cat_id=cat_id, image=filename)
        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/post')
        except:
            return render_template('post_create.html',context=context)
    else:
        return render_template('post_create.html',context=context)

    
@app.route('/post/delete/<int:id>')
def postDelete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/post')



def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION
       
if __name__=='__main__':
    app.run(debug=True)