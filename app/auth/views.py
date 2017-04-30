# Imports
from flask import flash, redirect, render_template, url_for, request, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
import pandas as pd
from werkzeug.utils import secure_filename
from bokeh.charts import Area, show
from bokeh.models import NumeralTickFormatter, HoverTool
from bokeh.io import output_file
import os

# Local Imports
import app
from . import auth
from .forms import LoginForm, RegistrationForm, UploadForm
from .. import db
from ..models import Analysis, User, File

# Global variables
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx', 'tsv'])
EXCEL_EXTENSIONS = ['.xls', '.xlsx']
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
        else:
            flash('File not supported. Please upload a csv or excel file type.')
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
    # Get file path and file extension
    file_path, file_extension = os.path.splitext(file_name)

    # Get file from server to process into data frame
    if file_extension == '.csv':
        # Load CSV file type
        df = pd.DataFrame(pd.read_csv(file, encoding="ISO-8859-1"))
    else:
        # Load files with excel based file extensions
        df = pd.DataFrame(pd.read_excel(file, encoding="ISO-8859-1"))

    # Render data frame as sample of entire data set
    df_head = df.head()

    return render_template('auth/uploads/file.html', name=file_name,
                           data=df_head.to_html(),
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


@auth.route('/analyses/view/<int:id>', methods=['GET'])
@login_required
def create_analysis(id):
    """
    View a pre-created analysis
    """
    # Get file path from database by id
    file = File.query.get_or_404(id).file

    # Get filename for template
    file_name = os.path.basename(file)
    # Get file path and file extension
    file_path, file_extension = os.path.splitext(file_name)

    # Get file from server to process into data frame
    if file_extension == '.csv':
        # Load CSV file type
        df = pd.DataFrame(pd.read_csv(file, encoding="ISO-8859-1", parse_dates=['Order Date']))
    else:
        # Load files with excel based file extensions
        df = pd.DataFrame(pd.read_excel(file, encoding="ISO-8859-1", parse_dates=['Order Date']))

    # Add columns for sales where profit is plus or zero to negative
    df_sales = df
    df_sales['Profitable'] = df['Sales'].where(df['Profit'] > 0, 0)
    df_sales['Unprofitable'] = df['Sales'].where(df['Profit'] <= 0, 0)

    # Filter only columns needed
    df_sales = df_sales[['Order Date', 'Customer Segment', 'Profit', 'Sales', 'Profitable', 'Unprofitable']]

    # Group by Segment
    df_sales2 = df_sales.groupby(['Customer Segment', 'Order Date']).sum()
    df_sales2 = df_sales2.reset_index(drop=False)

    # Group by Month
    df_mo = df_sales2.set_index('Order Date').groupby('Customer Segment').resample('M').sum()
    df_mo = df_mo.reset_index(drop=False)

    # Change column header to remove space for using as index
    df_segs = df_mo.rename(columns={'Customer Segment': 'Segment'})

    # Setting unique axis to pick up single Customer Segment
    cons_df = df_segs[df_segs['Segment'] == df_segs.Segment.unique()[0]]

    # Filter only columns for chart
    cons_df_area = cons_df[['Order Date', 'Profitable', 'Unprofitable']]

    # Reset index for chart axis labels
    cons_df_area = cons_df_area.set_index(['Order Date']).resample('M').sum()

    # When adding stack=True, Y labels skew.  Fixed with NumeralTickFormatter
    title1 = df_segs.Segment.unique()[0]
    cons_area = Area(cons_df_area, title=title1, legend="top_left",
                xlabel='', ylabel='Profit', plot_width=700, plot_height=400,
                stack=True,
                    )
    cons_area.yaxis[0].formatter = NumeralTickFormatter(format="0,00")

    data = show(cons_area)

    # this is a placeholder template
    return render_template('auth/analyses/render.html', data=data, title="Area Chart")
