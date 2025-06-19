from flask import render_template,Flask, request, redirect, url_for, flash, session
from functools import wraps
from flask import current_app as app #refers to the app.py-app object created
from .models import * #both resides in the same folder so no need to specify the path
import random
import string
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib

import re



def user_login_required(f):
    @wraps(f)
    def inner_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in first.', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.type == "user":
            flash('Login as User to View this page', 'danger')
            return redirect(url_for('admin'))
        return f(*args, **kwargs)
    return inner_function 

def admin_login_required(f):
    @wraps(f)
    def inner_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.type=="admin":
            flash('You are not authorized to view this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return inner_function

@app.route("/", methods=['GET', 'POST'])
@user_login_required
def index():
    user = User.query.get(session.get('user_id'))
    if user.type != 'admin':
        return render_template("index.html", user=user)
    else:
        return redirect(url_for('admin'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == '' or password == '':
            flash('Username or password cannot be empty.')
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist.Please register first.')
            return redirect(url_for('register'))
        if not user.check_password(password):
            flash('Incorrect username or password.')
            return redirect(url_for('login'))
        # If the user is found and password matches, set session
        session['user_id'] = user.user_id
        if user.type == 'admin':
            flash('Logged in successfully as admin.')
            return redirect(url_for('admin'))
        else:
            flash('Logged in successfully as user.')
            return redirect(url_for('index'))

    return render_template("login.html")




@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get("password")
        if username == '' or email == '' or password == '':
            flash('Username, email, and password cannot be empty.')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('User with this username already exists. Please choose some other username')
            return redirect(url_for('register'))
        user = User(username=username,email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('User successfully registered.')
        return redirect(url_for('login'))

  
    return render_template("register.html")
  
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

def duration_cost(price_per_hour, booked_at, released_at):
    # Make booked_at timezone-aware if it's naive
    if booked_at.tzinfo is None:
        booked_at = booked_at.replace(tzinfo=timezone.utc)

    duration = released_at - booked_at
    hours = duration.total_seconds() / 3600
    total_cost = round(hours * price_per_hour, 2)
    return total_cost

# def duration_cost(price_per_hour,booked_at,released_at):
#     duration = released_at - booked_at
#     hours = duration.total_seconds() / 3600
#     total_cost = round(hours * price_per_hour, 2)
#     return total_cost

@app.route("/release_dashboard/<int:r_id>",methods=['GET','POST'])
@user_login_required
def release_dashboard(r_id):
    current_reservation = Reservation.query.filter_by(r_id=r_id).first()
    spot_id = current_reservation.spot_id
    release_id = current_reservation
    lot_id = ParkingSpot.query.get(spot_id).lot_id
    lot = parkingLot.query.get(lot_id)
    price_per_hour = lot.price_per_hour
    booked_at = current_reservation.booked_at
    released_at = datetime.now(timezone.utc)
    total_cost = duration_cost(price_per_hour,booked_at,released_at)
    if request.method == 'POST':
        action = request.form.get("action")
        if action == "release":
            return redirect(url_for("release_spot", spot_id=spot_id, r_id=release_id.r_id))
        elif action == "cancel":
            flash('Release cancelled.', 'info')
            return redirect(url_for('user_dashboard'))
            # return redirect(url_for("release_dashboard",r_id=release_id.r_id))
        # release_id = current_reservation.r_id
        # return redirect(url_for(f"release_spot/{spot_id}/{release_id}"))
        # return redirect(url_for("release_spot", spot_id=spot_id, r_id=release_id))
            
            # return render_template("release_dashboard.html", user=User.query.get(session.get('user_id')),r_id=release_id, released_at=released_at, total_cost=total_cost)
    return render_template("release_dashboard.html", user=User.query.get(session.get('user_id')),
                           r_id=release_id,
                           spot_id=spot_id,
                           total_cost=total_cost,
                           released_at=released_at)



@app.route("/release_spot/<int:spot_id>/<int:r_id>", methods=['GET', 'POST'])
@user_login_required 
def release_spot(spot_id,r_id):
    current_reservation = Reservation.query.filter_by(r_id=r_id).first()
    if current_reservation.status == "booked":
        current_spot = ParkingSpot.query.filter_by(spot_id=spot_id).first()
        current_spot.status = "available"
        current_spot.start_time = None
        # reservation = Reservation.query.filter_by(spot_id=spot_id, status='booked').first()
        current_reservation.status = 'completed'
        current_reservation.released_at = datetime.now(timezone.utc)
        total_cost = 0
        if current_reservation.booked_at and current_reservation.released_at:
            lot = parkingLot.query.get(current_spot.lot_id)
            price_per_hour = lot.price_per_hour
            total_cost = duration_cost(price_per_hour, current_reservation.booked_at, current_reservation.released_at)
        current_reservation.total_cost = total_cost
        db.session.add(current_reservation)
        db.session.commit()
        flash(f"Spot {spot_id} has been released successfully.", 'success')
        return redirect(url_for('index'))
    else:
        flash(f"This Reservation is already completed.", 'warning')
        return redirect(url_for('user_dashboard'))
    return render_template("user_dashboard.html", user=User.query.get(session.get('user_id')),) 

@app.route("/booking_dashboard/<int:lot_id>", methods=['GET', 'POST'])
@user_login_required
def booking_dashboard(lot_id):
    spot_id = ParkingSpot.query.filter_by(status='available', lot_id= lot_id).first().spot_id if ParkingSpot.query.filter_by(status='available').first() else None
    if not spot_id:
        flash('No available parking spots found.', 'info')
        return redirect(url_for('user_lot_dashboard'))
    user_id = User.query.get(session.get('user_id'))
    spot_id = ParkingSpot.query.get(spot_id)
    lot_id = spot_id.lot_id
    # if request.method == 'POST':
    #     return redirect(url_for(f"book_spot/{user_id.user_id}/{spot_id.spot_id}/{lot_id.lot_id}"))
    return render_template("booking_dashboard.html", user=User.query.get(session.get('user_id')), user_id=user_id, spot_id=spot_id)
        
@app.route("/book_spot/<int:user_id>/<int:spot_id>/<int:lot_id>", methods=['GET', 'POST'])
@user_login_required
def book_spot(user_id, spot_id, lot_id):
    current_spot = ParkingSpot.query.get(spot_id)
    if request.method == 'POST':
        if request.form.get("action") == "cancel":
            return redirect(url_for('user_dashboard'))
        if current_spot.status == "available":
            current_spot.status = "occupied"
            booked_at = datetime.now(timezone.utc)
            current_spot.start_time = booked_at
            vehicle_number = request.form.get('vehicle_number')
            
            if not vehicle_number:
                flash('Vehicle number cannot be empty.', 'danger')
                return redirect(url_for('booking_dashboard', lot_id=lot_id, user_id=user_id, spot_id=spot_id))
            if Reservation.query.filter_by(vehicle_number=vehicle_number, status='booked').first():
                flash('This vehicle number is already booked.', 'danger')
                return redirect(url_for('booking_dashboard', user_id=user_id, spot_id=spot_id, lot_id=lot_id))
            status = 'booked'
            reservation = Reservation(user_id=user_id, spot_id=spot_id, vehicle_number=vehicle_number, status=status, booked_at=booked_at)
            db.session.add(reservation)
            db.session.commit()
            flash(f"Spot {spot_id} has been booked successfully.", 'success')
            return redirect(url_for('user_dashboard'))
    return render_template("user_dashboard.html", user=User.query.get(session.get('user_id')), spot_id=spot_id, lot_id=lot_id)

@app.route("/user_lot_dashboard", methods=['GET', 'POST'])
@user_login_required
def user_lot_dashboard():
    lots = parkingLot.query.all()
    lot_data = []

    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status='available').count()
        lot_data.append({
            'lot': lot,
            'available_spots': available_spots
        })
    # spots = ParkingSpot.query.filter_by(lot_id=lots[0].lot_id).all()
    # spot_count = ParkingSpot.query.filter_by(lot_id=lots.lot_id, status='available').all()
    return render_template("user_lot_dashboard.html", user=User.query.get(session.get('user_id')), lots=lot_data )

@app.route("/user_spot_dashboard/<int:lot_id>", methods=['GET', 'POST'])
@user_login_required
def user_spot_dashboard(lot_id):
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    lots = parkingLot.query.filter_by(lot_id=lot_id).all()
    print(spots)
    return render_template("user_spot_dashboard.html", user=User.query.get(session.get('user_id')), spots=spots, lots=lots)

@app.route("/user_dashboard")
@user_login_required
def user_dashboard():
    lots = parkingLot.query.all()
    reservation = Reservation.query.filter_by(user_id=session.get('user_id')).all()
    reservation_data = []
    lot_data = []

    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status='available').count()
        lot_data.append({
            'lot': lot,
            'available_spots': available_spots
        })
    for r in reservation:
        spot = ParkingSpot.query.get(r.spot_id)
        lot = parkingLot.query.get(spot.lot_id) if spot else None
        reservation_data.append({
        'reserve': r,
        'spot': spot,
        'lot': lot
        })
    return render_template("user_dashboard.html", user = User.query.get(session.get('user_id')), reservation=reservation_data, lot_data=lot_data)
 
@app.route("/view_profile", methods=['GET', 'POST'])
@user_login_required
def view_profile():
    user = User.query.get(session.get('user_id'))
    if request.method == 'POST':
        if request.form.get("action") == "update":
            return redirect(url_for('profile_update'))
        elif request.form.get("action") == "cancel":
            return redirect(url_for('index'))
    
    return render_template("view_profile.html", user=user)


@app.route("/profile_update", methods=['GET', 'POST'])
@user_login_required
def profile_update():
    user = User.query.get(session.get('user_id'))
    if request.method == 'POST':
        username = request.form.get('username')
        new_email = request.form.get('new_email')
        password = request.form.get('new_password')
        current_password = request.form.get('current_password')
        if username == '' or new_email=='' or password == '' or current_password == '':
            flash('Username or password cannot be empty.')
            return redirect(url_for('profile_update'))
        if User.query.filter_by(username=username).first() and username != user.username:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('profile_update'))
        user.username = username
        if User.query.filter_by(email=new_email).first() and new_email != user.email:
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('profile_update'))
        user.email = new_email
        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('profile_update'))
        user.password = password
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('index'))
    
    return render_template("profile_update.html", user=user)
 
@app.route("/search_results", methods=['GET', 'POST'])
@user_login_required
def search_results():
    search_query= request.args.get("search")
    if not search_query:
        flash('Search query cannot be empty.', 'danger')
        return redirect(url_for('user_lot_dashboard'))
        
    # Search for parking lots by location name or address
    results = parkingLot.query.filter(
            (parkingLot.location_name.ilike(f'%{search_query}%')) |
            (parkingLot.address.ilike(f'%{search_query}%'))
        ).all()
    lot_ids = [lot.lot_id for lot in results]
    available_spots = db.session.query(ParkingSpot.lot_id, db.func.count(ParkingSpot.spot_id))\
        .filter(ParkingSpot.lot_id.in_(lot_ids), ParkingSpot.status == 'available')\
        .group_by(ParkingSpot.lot_id)\
        .all()
    available_spots_dict = {lot_id: count for lot_id, count in available_spots}

    
    if not results:
        flash('No results found for your search.', 'info')
        return redirect(url_for('user_lot_dashboard'))
        
    return render_template("search_results.html", 
                           user=User.query.get(session.get('user_id')),
                           results=results, 
                           available_spots=available_spots_dict, 
                           search_query=search_query)
        
        
@app.route("/user_summary", methods=['GET'])
@user_login_required
def user_summary():
    user = User.query.get(session.get('user_id'))
    reservations = Reservation.query.filter_by(user_id=user.user_id).all()
    total_cost = sum(reservation.total_cost for reservation in reservations if reservation.total_cost)
    
    # Count the number of completed and ongoing reservations
    completed_count = sum(1 for reservation in reservations if reservation.status == 'completed')
    ongoing_count = sum(1 for reservation in reservations if reservation.status == 'booked')
    total_count = completed_count + ongoing_count
    
    #piechart
    #totalcost
    
    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f'{val}'  # just the raw value
        return my_autopct
    labels = ['Completed', 'Ongoing', 'Total Reservations']
    sizes = [completed_count, ongoing_count, total_count]
    colors = ['#66c2a5', '#fc8d62' ,'#e78ac3']
    explode = (0.1, 0.1, 0.1)
    plt.pie(sizes,labels=labels, colors=colors, autopct=make_autopct(sizes), startangle=140)
    plt.title("Statistics of Your Reservations")
    plt.savefig('static/user_summary_pie.png')
    plt.clf()
    
    
    
    return render_template("user_summary.html", 
                           user=user, 
                           total_count=total_count,
                           total_cost=total_cost, 
                           completed_count=completed_count, 
                           ongoing_count=ongoing_count)
# -----------------------admin routes----------------------------

        
# @app.route("/admin")
# @admin_login_required
# def admin():
#     lots = parkingLot.query.all()
#     lot_data = []
#     for lot in lots:
#         occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status='occupied').count()
#         total_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id).count()
#         available_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status='available').count()
#         lot_data.append({
#             'lot': lot,
#             'available_spots': available_spots
#             , 'occupied_spots': occupied_spots,
#             'total_spots': total_spots
#         })
#     return render_template("admin_dashboard.html", user = User.query.get(session.get('user_id')),
#                            lots=lot_data)

@app.route("/admin")
@admin_login_required
def admin():
    lots = parkingLot.query.all()
    lot_data = []
    for lot in lots:
        # Fetch all spots for the current lot
        all_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id).all()

        # Count status-based spots
        occupied_spots = sum(1 for spot in all_spots if spot.status == 'occupied')
        available_spots = sum(1 for spot in all_spots if spot.status == 'available')

        lot_data.append({
            'lot': lot,
            'spots': all_spots,  # Pass full list of spot objects
            'available_spots': available_spots,
            'occupied_spots': occupied_spots,
            'total_spots': len(all_spots)
        })

    return render_template("admin_dashboard.html",
                           user=User.query.get(session.get('user_id')),
                           lots=lot_data)



@app.route("/admin_profile_update", methods=['GET', 'POST'])
@admin_login_required
def admin_profile_update():
    user = User.query.get(session.get('user_id'))
    if request.method == 'POST':
        username = request.form.get('username')
        new_email = request.form.get('new_email')
        password = request.form.get('new_password')
        current_password = request.form.get('current_password')
        if username == '' or new_email=='' or password == '' or current_password == '':
            flash('Username or password cannot be empty.')
            return redirect(url_for('admin_profile_update'))
        if User.query.filter_by(username=username).first() and username != user.username:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('profile_update'))
        user.username = username
        if User.query.filter_by(email=new_email).first() and new_email != user.email:
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('profile_update'))
        user.email = new_email
        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('profile_update'))
        user.password = password
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('admin'))
    
    return render_template("admin_profile_update.html", user=user)
@app.route("/admin_view_profile", methods=['GET', 'POST'])
@admin_login_required
def admin_view_profile():
    user = User.query.get(session.get('user_id'))
    if request.method == 'POST':
        if request.form.get("action") == "update":
            return redirect(url_for('admin_profile_update'))
        elif request.form.get("action") == "cancel":
            return redirect(url_for('admin'))
    
    return render_template("admin_view_profile.html", user=user)

@app.route("/admin_add_lot", methods=['GET', 'POST'])
@admin_login_required
def admin_add_lot():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cancel':
            flash('Lot addition cancelled.', 'info')
            return redirect(url_for('admin'))
        if action == 'add':
            location_name = request.form.get('location_name')
            price_per_hour = request.form.get('price_per_hour')
            address = request.form.get('address')
            pincode = request.form.get('pincode')
            max_spots = request.form.get('max_spots')
            all_lots = parkingLot.query.filter_by(pincode=pincode).all()  # Get all parking lots with the same pincode
            existing_location_names = [lot.location_name.lower() for lot in all_lots]
            if location_name.lower() in existing_location_names:
                flash('A parking lot with this location name already exists in your city.', 'danger')
                return redirect(url_for('admin_add_lot'))
            # print("location_name:", location_name)
            # print("price_per_hour:", price_per_hour)
            # print("address:", address)
            # print("pincode:", pincode)
            # print("max_spots:", max_spots)
            if not location_name or not price_per_hour or not address or not pincode or not max_spots:
                flash('All fields are required.', 'danger')
                return redirect(url_for('admin_add_lot'))
            try:
                price_per_hour = float(price_per_hour)
                max_spots = int(max_spots)
            except ValueError:
                flash('Price per hour must be a number and max spots must be an integer.', 'danger')
                return redirect(url_for('admin_add_lot'))

            new_lot = parkingLot(location_name=location_name, price_per_hour=price_per_hour, address=address, pincode=pincode, max_spots=max_spots)
            db.session.add(new_lot)
            db.session.commit()
            for _ in range(max_spots):
                new_spot = ParkingSpot(lot_id=new_lot.lot_id, status='available')
                db.session.add(new_spot)

            db.session.commit()
            
            flash('Parking lot added successfully.', 'success')
            return redirect(url_for('admin'))
    
    return render_template("admin_add_lot.html", user=User.query.get(session.get('user_id')))

# @app.route("/admin_edit_lot/<int:lot_id>", methods=['GET', 'POST'])
@app.route("/admin_edit_lot/<int:lot_id>", methods=['GET', 'POST'])
@admin_login_required
def admin_edit_lot(lot_id):
    lot = parkingLot.query.filter_by(lot_id=lot_id).first()
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cancel':
            flash('Edit cancelled.', 'info')
            return redirect(url_for('admin'))

        if action == 'edit':
            location_name = request.form.get('location_name')
            price_per_hour = request.form.get('price_per_hour')
            address = request.form.get('address')
            pincode = request.form.get('pincode')
            max_spots_input = request.form.get('max_spots')

            # Validation
            if not location_name or not price_per_hour or not address or not pincode or not max_spots_input:
                flash('All fields are required.', 'danger')
                return redirect(url_for('admin_edit_lot', lot_id=lot_id))

            try:
                price_per_hour = float(price_per_hour)
                max_spots = int(max_spots_input)
            except ValueError:
                flash('Price per hour must be a number and max spots must be an integer.', 'danger')
                return redirect(url_for('admin_edit_lot', lot_id=lot_id))

            existing_locations = [l.location_name.lower() for l in parkingLot.query.filter_by(pincode=pincode).all() if l.lot_id != lot_id]
            if location_name.lower() in existing_locations:
                flash('A parking lot with this location name already exists in your city.', 'danger')
                return redirect(url_for('admin_edit_lot', lot_id=lot_id))

            # Update lot fields
            lot.location_name = location_name
            lot.price_per_hour = price_per_hour
            lot.address = address
            lot.pincode = pincode

            # Spot management
            existing_spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.spot_id).all()
            current_count = len(existing_spots)

            if max_spots > current_count:
                # Add new spots
                for _ in range(max_spots - current_count):
                    new_spot = ParkingSpot(lot_id=lot_id, status='available', start_time=None)
                    db.session.add(new_spot)

            elif max_spots < current_count:
                # Delete only if spot is available and has no reservation
                deletable_spots = []
                for spot in existing_spots[max_spots:]:
                    has_reservation = Reservation.query.filter_by(spot_id=spot.spot_id).first()
                    if spot.status == 'available' and not has_reservation:
                        deletable_spots.append(spot)

                if len(deletable_spots) < (current_count - max_spots):
                    flash('Cannot reduce spots. Not enough deletable (available & unused) spots.', 'danger')
                    return redirect(url_for('admin_edit_lot', lot_id=lot_id))

                for spot in deletable_spots:
                    db.session.delete(spot)

            lot.max_spots = max_spots
            db.session.commit()

            flash('Parking lot updated successfully.', 'success')
            return redirect(url_for('admin'))

    return render_template("admin_edit_lot.html", user=User.query.get(session.get('user_id')), lot=[lot])

@app.route("/admin_delete_lot/<int:lot_id>", methods=['GET', 'POST'])
@admin_login_required
def admin_delete_lot(lot_id):
    lot = parkingLot.query.filter_by(lot_id=lot_id).all()
    print(lot)
    # current_lot_spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    # # print(spots)
    available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='available').count()
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='occupied').count()
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cancel':
            flash('Deletion cancelled.', 'info')
            return redirect(url_for('admin'))
        if action == 'delete':
            if occupied_spots > 0:
                flash('Cannot delete lot with occupied spots.', 'danger')
                return redirect(url_for('admin'))
            db.session.delete(lot[0])
            db.session.commit()
            flash('Parking lot deleted successfully.', 'success')
            return redirect(url_for('admin'))
    
    return render_template("admin_delete_lot.html", user=User.query.get(session.get('user_id')), lot=lot, 
                           available_spots=available_spots, 
                           occupied_spots=occupied_spots)
    
@app.route("/admin_view_spots/<int:lot_id>/<int:spot_id>", methods=['GET','POST'])
@admin_login_required
def admin_view_spots(lot_id, spot_id):
    selected_spot = ParkingSpot.query.filter_by(lot_id=lot_id, spot_id=spot_id).all()
    if not selected_spot:
        flash('Parking spot not found.', 'danger')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            flash('Returning to Admin dashboard.', 'info')
            return redirect(url_for('admin'))
        elif action == 'view':
            # flash('Viewing parking spot details.', 'success')
            return redirect(url_for('admin_view_spots_details', lot_id=lot_id, spot_id=spot_id))
    # If the request method is GET, render the admin_view_spots template 
    status = ParkingSpot.query.filter_by(lot_id=lot_id, spot_id=spot_id).first().status
    return render_template("admin_view_spots.html", 
                           user=User.query.get(session.get('user_id')), 
                           spot=selected_spot,
                           status=status)

@app.route("/admin_view_spots_details/<int:lot_id>/<int:spot_id>", methods=['GET'])
@admin_login_required
def admin_view_spots_details(lot_id, spot_id):
    selected_spot = ParkingSpot.query.filter_by(lot_id=lot_id, spot_id=spot_id).first()
    if not selected_spot:
        flash('Parking spot not found.', 'danger')
        return redirect(url_for('admin'))
    
    reservations = Reservation.query.filter_by(spot_id=spot_id,status="booked").all()
    
    current_reservation = Reservation.query.filter_by(spot_id=spot_id,status="booked").first()
    spot_id = current_reservation.spot_id
    lot_id = ParkingSpot.query.get(spot_id).lot_id
    lot = parkingLot.query.get(lot_id)
    price_per_hour = lot.price_per_hour
    booked_at = current_reservation.booked_at
    released_at = datetime.now(timezone.utc)
    total_cost = duration_cost(price_per_hour,booked_at,released_at)
    
    return render_template("admin_view_spots_details.html", 
                           user=User.query.get(session.get('user_id')), 
                           spot=selected_spot, 
                           reservations=reservations,
                           total_cost=total_cost)



@app.route("/admin_search_results", methods=['GET', 'POST'])
@admin_login_required
def admin_search_results():
    search_word= request.args.get("search")
    key= request.args.get("key")
    if not search_word:
        flash('Search query cannot be empty.', 'danger')
        return redirect(url_for('admin'))
    admin_user_id = session.get('user_id')
    admin_username = User.query.get(admin_user_id).username
    if key == "username" and search_word == admin_username.lower():
        flash('You cannot search for your own username.', 'warning')
        return redirect(url_for('admin'))
    elif key == "user_id" and search_word == str(admin_user_id):
        flash('You cannot search for your own user ID.', 'warning')
        return redirect(url_for('admin'))
    else:
        if key == "lot_location":
            results = parkingLot.query.filter(
                (parkingLot.location_name.ilike(f'%{search_word}%')) |
                (parkingLot.address.ilike(f'%{search_word}%'))
            ).all()
            lots = parkingLot.query.filter(
                (parkingLot.location_name.ilike(f'%{search_word}%')) |
                (parkingLot.address.ilike(f'%{search_word}%'))
            ).all()
            lot_data = []
            for lot in lots:
        # Fetch all spots for the current lot
                all_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id).all()

                # Count status-based spots
                occupied_spots = sum(1 for spot in all_spots if spot.status == 'occupied')
                available_spots = sum(1 for spot in all_spots if spot.status == 'available')

                lot_data.append({
                    'lot': lot,
                    'spots': all_spots,  # Pass full list of spot objects
                    'available_spots': available_spots,
                    'occupied_spots': occupied_spots,
                    'total_spots': len(all_spots)
                })
        elif key == "user_id":
            results = User.query.filter((User.user_id.ilike(f'%{search_word}%'))).all()
        elif key == "username":
            results = User.query.filter((User.username.ilike(f'%{search_word}%'))).all()
    
    
    return render_template("admin_search_results.html",
                           user=User.query.get(session.get('user_id')),
                           results=results, 
                           search_word=search_word, 
                           key=key,
                           lots=lot_data)
    
    
@app.route("/admin_users", methods=['GET', 'POST'])
@admin_login_required
def admin_users():
    users = User.query.filter(User.user_id != 1).all()
    return render_template("admin_users.html",
                           user=User.query.get(session.get('user_id')),
                           users=users)
    