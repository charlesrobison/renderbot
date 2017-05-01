# Imports
from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    """
    Create a User table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    file = db.relationship('File', backref='users')

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class File(db.Model):
    """
    Create a files table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(200), index=True)
    file_type = db.Column(db.String(200), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    analysis = relationship('Analysis', uselist=False, backref='files')

    def __repr__(self):
        return '<File: {}>'.format(self.file)


class Analysis(db.Model):
    """
    Create an analysis table
    """

    __tablename__ = 'analyses'
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(200), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    source_file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    source_file = relationship('File', backref='analyses')

    def __repr__(self):
        return '<Analysis: {}>'.format(self.analysis_file)
