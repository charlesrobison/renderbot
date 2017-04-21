# Imports
from flask import flash, redirect, render_template, url_for, request, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
import pandas as pd
from werkzeug.utils import secure_filename
import os

# Local Imports
import app
from . import auth
from .forms import LoginForm, RegistrationForm, UploadForm
from .. import db
from ..models import User, File

# Global variables
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx', 'tsv'])
UPLOAD_FOLDER = '/tmp/renderbot_uploads'


#  Determine if allowed file type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data)

        # add user to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log a user in through the login form
    """
    form = LoginForm()

    if form.validate_on_submit():

        # check whether user exists in the database and whether
        # the password entered matches the password in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(
                form.password.data):
            # log employee in
            login_user(user)

            # redirect to the dashboard page after login
            return redirect(url_for('home.dashboard'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log a user out through the logout link
    """

    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))


#  File Upload Views


@auth.route('/uploads/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """
    Handle file uploads
    """

    upload_file = True

    form = UploadForm()

    if request.method == 'POST':
        file = request.files['file']

        # save to app server (adjust path at top)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # add file name to the database
            form_filename = File(file=file_path,
                                 user_id=current_user.id)
            db.session.add(form_filename)
            db.session.commit()
            flash('You have uploaded {}.'.format(filename))
            return redirect(url_for('auth.list_uploads'))

    # load upload template
    return render_template('auth/uploads/upload.html',
                           action="Upload",
                           upload_file=upload_file,
                           form=form, title='Upload File')


@auth.route('/uploads/uploads', methods=['GET', 'POST'])
@login_required
def list_uploads():
    """
    List all user uploads
    """

    uploads = File.query.filter_by(user_id=current_user.id)

    return render_template('auth/uploads/uploads.html',
                           uploads=uploads, title="Uploads")

@auth.route('/uploads/upload/<id>')
@login_required
def single_file(id):
    """
    Renders preview of selected file
    """

    # Get file path from database by id
    file = File.query.get_or_404(id).file

    # Get filename for template
    file_name = os.path.basename(file)

    # Get file from server to process into data frame
    df = pd.DataFrame(pd.read_csv(file, encoding="ISO-8859-1"))

    return render_template('auth/uploads/file.html', name=file_name,
                           data=df.to_html(),
                           title="Data Preview")


@auth.route('/uploads/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_upload(id):
    """
    Delete a user file record / user access to the file (not an actual file) from the database
    """

    uploads = File.query.get_or_404(id)
    db.session.delete(uploads)
    db.session.commit()
    flash('You have successfully deleted the file.')

    # redirect to the uploads page
    return redirect(url_for('auth.list_uploads'))

    return render_template(title="Delete File")
