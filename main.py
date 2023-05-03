import os

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

from flask_migrate import Migrate
from flask_gravatar import Gravatar

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

import datetime
from functools import wraps
#WTF FORM IMPORT
from forms import CreatePostForm, UserFormRegister, UserFormLogin, CommentForm

####contact form imports########
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

admin_user = False
admin_user_name = None
current_user = None
index_dlt=None

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '8BYkEfBA6O6donzWlSihBXox7C0sKR6b')
#'8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)
Bootstrap(app)
# ckeditor.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "sqlite:///blog.db")
#'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)

gravatar = Gravatar(
                    app,
                    size=60,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None

)
Base = declarative_base()
##CONFIGURE TABLE
class BlogPost(db.Model, Base):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    comments = relationship("Comment", back_populates="parent_post")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    # author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


    def to_dict(self):
        # Method 1.
        dictionary = {}

        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary




class User(UserMixin, db.Model, Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
#Line below only required once, when creating DB.


class Comment(db.Model, Base):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    parent_post = relationship("BlogPost", back_populates="comments")


    body = db.Column(db.Text, nullable=False)

db.create_all()



# @app.errorhandler(403)
# def page_not_found():
#     # note that we set the 404 status explicitly
#     return render_template('403.html'), 403

# "<h2>You are not authorised as Admin. More and More Secure In Life!!</h2>"
def admin_only(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if not admin_user:
            return abort(403)
        return func(*args, **kwargs)

    return wrapper_function



@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    # db.session.query(BlogPost).delete()
    # db.session.query(User).delete()
    # db.session.query(Comment).delete()
    # db.session.commit()
    return render_template("index.html", all_posts=posts, logged_in=True, admin_user=admin_user, current_user=current_user)


@app.route("/post/<int:index>", methods=['GET', 'POST'])
def show_post(index):
    global index_dlt
    global current_user
    requested_post = None
    requested_post_author = None
    index_dlt=index
    posts = db.session.query(BlogPost).all()
    for post in posts:
        if post.id == index:
            requested_post_author = post.author.name
            print(requested_post_author)

        print(post.id)
    result = [items.to_dict() for items in posts]
    print(result)
    for blog_post in result:
        print(blog_post)

        if blog_post["id"] == index:
            requested_post = blog_post
            comments = Comment.query.filter_by(post_id=index)
            # result = [items for items in comments]
            # print(result)

    form = CommentForm()
    print(current_user)

    if form.validate_on_submit():
        # if not current_user.is_authenticated:
        #     flash("You need to login or register to comment.")
        #     return redirect(url_for("login"))
        new_comment = Comment(

            body=request.form['body'],
            parent_post=BlogPost.query.get(index),
            comment_author=User.query.filter_by(name=current_user).first()


        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(f'/post/{index}')
        # for post in posts:
        #     print(post.body)
        # return render_template('post.html', form=form, posts=comments, post=requested_post, author_name=requested_post_author, logged_in=True, admin_user=admin_user)



    return render_template("post.html", form=form, comments=comments, post=requested_post,
                           author_name=requested_post_author, logged_in=True, admin_user=admin_user, current_user=current_user, admin_user_name=admin_user_name)


@app.route("/edit-post/<int:id>", methods=['GET', 'POST'])
@admin_only
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
        author=post.author.name,
        body=post.body
    )

    if edit_form.validate_on_submit():
        print('true')

        post.title = request.form['title']
        post.subtitle = request.form['subtitle']
        post.img_url = request.form['img_url']
        post.author.name = request.form['author']
        post.body = request.form['body']
        post.date = result_date



        db.session.commit()
        return redirect('/')

    return render_template("make-post.html", form=edit_form, requested_post=requested_post, logged_in=True, current_user=current_user )


@app.route("/new-post", methods=['GET', 'POST'])
@admin_only
def new_post():

    form = CreatePostForm()

    if form.validate_on_submit():
        #current_user = User.query.get(id)
        print(current_user)
        x = datetime.datetime.now()
        result_date = x.strftime("%B") + ' ' + x.strftime("%d") + ',' + x.strftime("%Y")
        print(result_date)
        new_blog = BlogPost(
            title=request.form['title'],
            subtitle=request.form['subtitle'],
            author=User.query.filter_by(name=current_user).first(),
            date=result_date,
            img_url=request.form['img_url'],
            body=request.form['body'],

        )

        db.session.add(new_blog)
        db.session.commit()

        return redirect('/')



    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/delete-post/<int:id>")
def delete_post(id):

    post = BlogPost.query.get(id)
    db.session.delete(post)
    db.session.commit()

    return redirect('/')

@app.route("/delete-user/<int:id>")
def delete_user(id):

    post = User.query.get(id)
    db.session.delete(post)
    db.session.commit()

    all_rest_of_users = [items for items in User.query.all()]
    print(all_rest_of_users)

    return redirect('/')


@app.route('/delete-comment/<int:id>')
def delete_comment(id):
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()

    # db.session.query(BlogPost).delete()
    # db.session.query(User).delete()
    # db.session.query(Comment).delete()
    # db.session.commit()
    return redirect(f'/post/{index_dlt}')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserFormRegister()

    if form.validate_on_submit():
        users = User.query.all()
        all_emails = [item.email for item in users]
        print(all_emails)
        if request.form['email'] not in all_emails:
            new_user = User(
                email=request.form['email'],
                password=generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8),
                name=request.form['name'],

            )
            db.session.add(new_user)
            db.session.commit()

            posts = db.session.query(BlogPost).all()
            return render_template('index.html', all_posts=posts, logged_in=True, current_user=current_user)

        else:
            flash('the email is already used before. Please try others!!')
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global admin_user_name
    form = UserFormLogin()
    # admin_user = False
    global admin_user
    global current_user
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form['email']).first()
        print(user)

        if user:
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                flash('Logged in successfully.')
                posts = db.session.query(BlogPost).all()
                users = User.query.all()
                all_users_id = [item.id for item in users]
                print(all_users_id)

                current_user = user.name
                print(current_user)

                if user.id == 1:
                    admin_user = True
                    admin_user_name=current_user
                print(admin_user)
                return render_template('index.html', all_posts=posts, logged_in=True, admin_user=admin_user, current_user=current_user)
            else:

                if request.form['email'] != user.email or \
                        request.form['password'] != user.password:
                    flash('Wrong password or email. Keep try again..!!')
                else:
                    flash('You were successfully logged in')
                    return redirect(url_for('/'))

        else:

            flash('The User does not exist. Try again please!!')


    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/about")
@login_required
def about():
    print(current_user)
    return render_template("about.html", logged_in=True, current_user=current_user)


@app.route("/contact", methods=['GET', 'POST'])
@login_required
def contact():
    sending_email_form = False
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "jonsnow9091.fs@gmail.com"  # Enter your address
    # sender_email = None  # Enter receiver address
    password = "piqsebtpohevyzin"

    if request.method == "POST":
        print(request.form)
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message_blg = request.form['message']

        context_of_blog_form = []
        context_of_blog_form.append(name)
        context_of_blog_form.append(phone)
        context_of_blog_form.append(message_blg)

        receiver_email = [email]

        print(name + email + phone + message_blg)

        message = MIMEMultipart("alternative")
        message["Subject"] = "Blog Community Contact Form"
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)

        # formatted_articles = [f"\n Via Countries : {value}" \
        #                       for value in context_of_blog_form]
        #
        # print(formatted_articles)

        if receiver_email:


            text = """\
    
                        The Best Advertising!!
    
                       """

            html = """\
                           <html>
                             <body>
                              <h1>
                              Costumer Mailed to you!!!
                              Please Attention..
                               </h1>
    
                             </body>
                           </html>
                           """ + f'<p><span>Costumer Name:</span> {name}\n</p>' \
                               + f'<p><span>Costumer Phone:</span> {phone}\n</p>' \
                               + f'<p><span>Costumer Message:</span> {message_blg}\n</p>' \


            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)



            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
                sending_email_form = True
            # print(message.as_string())


            return render_template("contact.html", logged_in=True, current_user=current_user, sending_email_form=sending_email_form)
    return render_template("contact.html", logged_in=True, current_user=current_user)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)