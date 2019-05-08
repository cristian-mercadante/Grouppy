from grouppy import db
from flask_login import UserMixin

bepartof = db.Table(
    'bepartof',
    db.Column('user_id', db.Integer,
              db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer,
              db.ForeignKey('company.id')),
    db.Column('is_admin', db.Boolean,
              default=False, nullable=False)
)

goout = db.Table(
    'goout',
    db.Column('user_id', db.Integer,
              db.ForeignKey('user.id')),
    db.Column('trip_id', db.Integer,
              db.ForeignKey('trip.id')),
    db.Column('is_driving', db.Boolean,
              default=False, nullable=False)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile_pic = db.Column(
        db.String(20), default='default.jpg', nullable=False)
    name = db.Column(db.String(20))
    surname = db.Column(db.String(20))
    bio = db.Column(db.String(256))
    companies = db.relationship('Company', secondary=bepartof,
                                backref=db.backref('groups'))


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    users = db.relationship('User', secondary=bepartof,
                            backref=db.backref('users_in_company'))
    trips = db.relationship(
        'Trip', backref=db.backref('trips'))


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    title = db.Column(db.String(20), nullable=False)
    origin = db.Column(db.String(20), nullable=False)
    destination = db.Column(db.String(20), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    a_r = db.Column(db.Boolean, nullable=False)
    drink = db.Column(db.Boolean, nullable=False)
    disco = db.Column(db.Boolean, nullable=False)
    vacation = db.Column(db.Boolean, nullable=False)
    driver_paid = db.Column(db.Boolean, nullable=False)
    users = db.relationship('User', secondary=goout,
                            backref=db.backref('users_in_trip'))
