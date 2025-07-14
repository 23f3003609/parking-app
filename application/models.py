from flask_sqlalchemy import SQLAlchemy
from .database import db
from datetime import datetime, timezone
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    hpassword = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False, unique=True)
    type = db.Column(db.String(), nullable=False, default='user')
    
    #relationship
    reservations = db.relationship('Reservation', backref='user', lazy=True, foreign_keys='Reservation.user_id')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.hpassword = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hpassword, password)
    
    
    
class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    lot_id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(), nullable=False)
    pincode = db.Column(db.String(), nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    is_lot_active = db.Column(db.Boolean, nullable=False, default=True)
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True)
    



class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    spot_id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id'), nullable=False)
    status = db.Column(Enum('available', 'occupied', name='spot_status'), nullable=False, default='available')
    start_time = db.Column(db.DateTime, nullable=True)
    is_spot_active = db.Column(db.Boolean, nullable=False, default=True)
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, foreign_keys='Reservation.spot_id')
    
    
    
class Reservation(db.Model):
    __tablename__ = 'reservation'
    r_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.spot_id'), nullable=False)
    vehicle_number = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False, default='booked')
    booked_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    released_at = db.Column(db.DateTime, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)