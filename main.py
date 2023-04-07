from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)
Bootstrap(app)
# ckeditor.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        # Method 1.
        dictionary = {}

        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    posts = db.session.query(BlogPost).all()
    result = [items.to_dict() for items in posts]
    print(result)
    for blog_post in result:
        print(blog_post)
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/edit-post/<int:id>", methods=['GET', 'POST'])
def edit_post(id):
    x = datetime.datetime.now()
    result_date = x.strftime("%B") + ' ' + x.strftime("%d") + ',' + x.strftime("%Y")
    requested_post = True
    post = BlogPost.query.get(id)
    print(post.title)

    #this is very good point of existing data on form is to be able to seem there!!!!!!
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )

    if edit_form.validate_on_submit():
        print('true')

        post.title = request.form['title']
        post.subtitle = request.form['subtitle']
        post.img_url = request.form['img_url']
        post.author = request.form['author']
        post.body = request.form['body']
        post.date = result_date



        db.session.commit()
        return redirect('/')

    return render_template("make-post.html", form=edit_form, requested_post=requested_post )


@app.route("/new-post", methods=['GET', 'POST'])
def new_post():

    form = CreatePostForm()

    if form.validate_on_submit():
        print('True')
        x = datetime.datetime.now()
        result_date = x.strftime("%B") + ' ' + x.strftime("%d") + ',' + x.strftime("%Y")
        print(result_date)
        new_blog = BlogPost(
            title=request.form['title'],
            subtitle=request.form['subtitle'],
            author=request.form['author'],
            date=result_date,
            img_url=request.form['img_url'],
            body=request.form['body'],

        )

        db.session.add(new_blog)
        db.session.commit()

        return redirect('/')



    return render_template("make-post.html", form=form)


@app.route("/delete-post/<int:id>")
def delete_post(id):

    post = BlogPost.query.get(id)
    db.session.delete(post)
    db.session.commit()

    return redirect('/')

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)