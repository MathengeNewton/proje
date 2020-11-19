from flask import Flask, render_template, url_for, session, redirect, jsonify, request, flash
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from flask_bcrypt import Bcrypt
import time
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mathenge,./1998@localhost/mainapp'
app.config['SECRET_KEY'] = 'some=secret+key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
UPLOAD_FOLDER = os.getcwd() + '/static/uploads/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
from models import * 

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(imageFile):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in imageFile:
            print('No file part')
            return None

        file = imageFile['file']

        # if user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return None
        if file and allowed_file(file.filename):
            img = Image.open(file)
            new_width = 150
            new_height = 150
            size = (new_height, new_width)
            img = img.resize(size)
            stamped = int(time.time())
            print('all good')
            img.save(os.path.join(UPLOAD_FOLDER, str(stamped) + file.filename))
            print(os.path.join(UPLOAD_FOLDER, str(stamped) + file.filename))
            return '/static/uploads/images/' + str(stamped) + file.filename
        else:
            return None

# customer landing page
@app.route('/', methods=['POST', 'GET'])
def main():
    return render_template('dash.html')

@app.route('/rentals', methods=['POST', 'GET'])
def rental_home():
    allrentals = Property.fetch_by_status_occupied()
    return render_template('rentals.html', allrentals=allrentals)

@app.route('/property-for-sale', methods=['POST', 'GET'])
def sales_home():
    allrentals = Property.fetch_vacant_sales_property()
    return render_template('sales.html', allrentals=allrentals)

# log in page is initiated here
@app.route('/gateway')
def start():
    return render_template('index.html')

# owner register and login
@app.route('/owner/register')
def owner_register():
    return render_template('adminreg.html')
# owner registration occurs
@app.route('/owner_reg', methods=['POST', 'GET'])
def owner_reg():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            confirmpass = request.form['confirmpass']        
            if password != confirmpass:
                flash('Passwords dont match', 'danger')
                return redirect(url_for('owner_register'))
            elif(Users.check_users_exists(email)):
                flash('Email already in use', 'danger')
                return redirect(url_for('owner_register'))
            else:
                hashpassword = bcrypt.generate_password_hash(
                    password).decode('utf-8')

                y = Users(name=name, email=email,
                        phone_number=phone, role = "owner",password=hashpassword)
                y.insert_record()

                flash('Account successfully created', 'success')
                return redirect(url_for('owner_login'))
        except Exception as e:
            print(e)
            flash('An error occured','danger')
            return redirect(url_for('owner_register'))

    return redirect(url_for('owner_register'))

# owner login
@app.route('/owner/login')
def owner_login():
    return render_template('adminlogin.html')


@app.route('/owner/log_in', methods=['GET', 'POST'])
def Owners_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if Users.check_users_exists(email):
            if Users.validate_password(email=email, password=password):                
                session['email'] = email
                session['uid'] = Users.get_user_id(email)
                role = Users.get_user_role(session['uid'])
                session['role'] = role
                return redirect(url_for('admin'))
            else:
                flash('Invalid login credentials', 'danger')
                return redirect(url_for('owner_login'))
        else:
            flash('Invalid login credentials', 'danger')
            return redirect(url_for('owner_login'))
    # except Exception as e:
        # print(e)
    return render_template('owner_login.html')
# customer registration render page
@app.route('/registration')
def registration():
    return render_template('register.html')

# customer registration
@app.route('/cust_reg', methods=['POST', 'GET'])
def cust_reg():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            confirmpass = request.form['confirmpass']

            if password != confirmpass:
                flash('Passwords dont match', 'danger')
                return redirect(url_for('registration'))
            elif(Users.check_users_exists(email)):
                flash('Email already in use', 'danger')
                return redirect(url_for('regisration'))
            else:
                hashpassword = bcrypt.generate_password_hash(
                    password).decode('utf-8')
                session['myemail'] = email
                session['phone'] = phone
                y = Users(name=name, email=email,
                            phone_number=phone,role = "customer", password=hashpassword)
                y.insert_record()
                uid = Users.get_user_id_by_email_role(email,"customer")
                wallet = Wallet(client_id=uid)
                wallet.insert_record()
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Error creating user. Try again later','danger')
            return redirect(url_for('registration'))
    else:
        flash('Try again','danger')
        return redirect(url_for('registration'))



@app.route('/book-to-rent/<int:pid>', methods=['POST'])
def book_to_rent(pid):
    if 'custemail' in session:
        try:
            custid = session['custid']           
            e = session['custemail']
            balance = Wallet.get_client_balance(custid)
            rental_owner = Property.get_rental_owner_by_id(pid)
            price = Property.get_rental_price(pid)
            final_price = price * 2
            if balance >= final_price: 
                tnow = datetime.datetime.now()
                createbooking = Bookings(rental_id = pid,customer_email = e,booking_date = tnow)
                createbooking.insert_record()
                y = Payments(to_=rental_owner,from_=custid,amount = final_price,date = tnow)
                y.insert_record()
                updaterental = Property.update_rental_by_id(pid)
                updatewallet = Wallet.reduce_balance_by_client_id(custid,final_price)
                flash('Booking reservation made','success')
                return redirect(url_for('main'))
            else:
                flash('Please recharge your wallet and try again.','danger')
                return redirect(url_for('profile'))
        except Exception as e:
            print(e)
            flash('Booking failed','danger')
            return redirect(url_for('main'))

    else:
        return redirect(url_for('login'))


@app.route('/book-to-buy/<int:pid>', methods=['POST'])
def book_to_buy(pid):
    if 'custemail' in session:
        try:
            custid = session['custid']   
            print(custid)        
            e = session['custemail']
            balance = Wallet.get_client_balance(custid)
            rental_owner = Property.get_rental_owner_by_id(pid)
            price = Property.get_rental_price(pid)
            final_price = price / 2
            if balance >= final_price: 
                tnow = datetime.datetime.now()
                createbooking = Bookings(rental_id = pid,customer_email = e,booking_date = tnow)
                createbooking.insert_record()
                y = Payments(to_=rental_owner,from_=custid,amount = final_price,date = tnow)
                y.insert_record()
                updaterental = Property.update_rental_by_id(pid)
                updatewallet = Wallet.reduce_balance_by_client_id(custid,final_price)
                flash('Booking reservation made','success')
                return redirect(url_for('profile'))
            else:
                flash('Please recharge your wallet and try again.','danger')
                return redirect(url_for('profile'))
        except Exception as e:
            print(e)
            flash('Booking failed','danger')
            return redirect(url_for('main'))

    else:
        return redirect(url_for('login'))


# customer login render template
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/tenant/login', methods=['GET', 'POST'])
def tenant_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if Users.check_users_exists(email):
            if Users.validate_password(email=email, password=password):
                session['custemail'] = email
                session['custid'] = Users.get_user_id(email)   
                role = Users.get_user_role(session['custid'])
                session['role'] = role
                return redirect(url_for('main'))
            else:
                flash('Invalid login credentials', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Invalid login credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')



@app.route('/admin')
def admin():
    if 'role' in session:
        if session['role'] == "owner":
            return render_template('admindash.html')
        else:
            flash('You are not clered to use this dashboard','danger')
            return redirect(url_for('owner_login'))
    else:
        return redirect(url_for('owner_login'))


@app.route('/rentals/status', methods=['POST', 'GET'])
def rental_status():
    if 'email' in session:
        allr = Bookings.fetch_all()
        return render_template('rentalstatus.html', allr=allr)
    else:
        return redirect(url_for('owner_login'))



@app.route('/rentals/status/clear')
def clear_status():
    if 'email' in session:
        Bookings.delete_all()
        return redirect(url_for('rental_status'))
    else:
        return redirect(url_for('owner_login'))
        


@app.route('/payments', methods=['GET', 'POST'])
def payments_all():
    if 'uid' in session:
        myid=session['uid']
        print(myid)
        payments = Payments.owner_payments(myid)
        print('payments: ',payments)
        return render_template('payments.html', payments=payments)
    else:
        return redirect(url_for('owner_login'))

@app.route('/rentals/all', methods=['GET', 'POST'])
def rentals_all():
    if 'email' in session:
        allr = Property.fetch_all()
        print(allr)
        return render_template('allrentals.html', allr=allr)
    else:
        return redirect(url_for('owner_login'))

@app.route('/view/bookings/<int:fid>')
def view_booking(fid):
    if 'email' in session:
        try:
            details = Bookings.get_booking_by_id(fid)
            if details:
                mylist = []
                mydict = {'id':details.id}         
                rid = details.rental_id
                rdets  = Property.get_rental_by_id(rid)
                mydict['image'] = rdets.img               
                customer = details.customer_email
                print('customer: ',customer)
                customerdets = Users.get_user_by_email(customer)
                for obj in customerdets:
                    print('user: ',obj)
                    mydict['customer'] = obj.name
                    mydict['customer_phone'] = obj.phone_number 
                mylist.append(mydict)
                print('mydict: ',mylist)
                return render_template('bookingdetails.html',details = mylist)
            else:
                flash('No data available','danger')
                return render_template('bookingdetails.html')
        except Exception as e:
            print(e)
            flash('Error retreiving data','danger')
            return render_template('bookingdetails.html')
    else:
        return redirect(url_for('owner_login'))

@app.route('/rental-details/<int:rid>')
def rental_details(rid):
    if 'email' in session:
        rentaldets = Property.get_rental_detail_by_id(rid)
        return render_template('rentaldetail.html',allr = rentaldets)
    else:
        return redirect(url_for('owner_login'))

@app.route('/update/<int:rid>')
def rental_update_page(rid):
    if 'email' in session:
        rentaldets = Property.get_rental_detail_by_id(rid)
        return render_template('rentalupdate.html',details = rentaldets)
    else:
        return redirect(url_for('owner_login'))



@app.route('/updaterental/<int:rid>' ,methods=['POST'])
def update_rental_details(rid):
    if 'email' in session:
        location = request.form['location']
        description = request.form['description']
        price = request.form['price']
        status = request.form['status']
        update = Property.update_rental_details(rid,location,description,price,status)
        rentaldets = Property.get_rental_by_id(rid)
        if update:
            rentaldets = Property.get_rental_detail_by_id(rid)
            flash('Update complete.','success')
            return render_template('rentaldetail.html',allr = rentaldets)
        else:
            flash('Update not done. Please try again later','danger')
            return render_template('rentalupdate.html') 
    else:
        return redirect(url_for('owner_login'))
        


@app.route('/home', methods=['GET', 'POST'])
def upload_rental():
    if 'email' in session:
        if request.method == 'POST':
            print(session['email'])
            image_url = upload_file(request.files)
            location = request.form['location']
            description = request.form['description']
            category = request.form['category']
            house_type = request.form['housetype']
            price = request.form['price']
            ownerid = session['uid']          
            x = Property(img=image_url, location=location,
                            description=description, price=price,owner = ownerid,house_type = house_type,category = category)
            x.insert_record()       

            print('record successfully added')

            return render_template('admindash.html')
    else:
        return redirect(url_for('owner_login'))

    return render_template('admindash.html')

# rental booking
@app.route('/rental-book/<int:pid>', methods=['POST'])
def bid(pid):
    if 'custemail' in session:
        if request.method == 'POST':            
            email = session['custemail']   
            id = Users.get_user_id(email)
            thisrental = Property.get_rental_detail_by_id(pid)
            for rental in thisrental:
                price = rental.price
                doubleprice = int(price) * 2
            ownerid = Property.get_rental_owner_by_id(pid)
            owner = Users.get_user_details_by_id(ownerid)
            print(owner)
            return render_template('checkout.html', thisrental=thisrental,Owners = owner,doubleprice = doubleprice)
        else:
            return redirect(url_for('main'))

    else:
        return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'custid' in session:
        email = session['custemail']
        id = session['custid']
        userdetails = Users.get_user_by_email(email)
        print('userdetails',userdetails)
        wallet = Wallet.get_record_by_client(id)
        return render_template('profile.html',details = userdetails,wallet = wallet)
    else:
        return redirect(url_for('login'))


@app.route('/wallet-recharge/<int:id>')
def simulate_recharge(id):
    if 'custid' in session:
        return render_template('rechargewallet.html',uid = id)
    else:
        return redirect(url_for('login'))

@app.route('/recharge',methods = ['POST'])
def recharge():
    if 'custid' in session:    
        try:    
            user = request.form['user']
            amount = request.form['amount']
            recharge = Wallet.increase_balance_by_client_id(user,amount)
            flash('Recharge succesiful','success')
            return redirect(url_for('profile'))
        except:
            flash('Recharge failed. Try again later','danger')
            return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))

@app.route('/purchase-book/<int:pid>', methods=['POST'])
def purchase_book(pid):
    if 'custemail' in session:
        if request.method == 'POST':            
            email = session['custemail']   
            id = Users.get_user_id(email)
            thisrental = Property.get_rental_detail_by_id(pid)
            for rental in thisrental:
                price = rental.price
                halfprice = int(price) / 2
            ownerid = Property.get_rental_owner_by_id(pid)
            owner = Users.get_user_details_by_id(ownerid)
            return render_template('purchase.html', thisrental=thisrental,Owners = owner,halfprice = halfprice)
        else:
            return redirect(url_for('main'))

    else:
        return redirect(url_for('login'))

# delete a product
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    deleted = Property.delete_by_id(id)
    if deleted:
        flash("Deleted Succesfully", 'success')
        return redirect(url_for('rentals_all'))
    else:
        flash("Record not found", 'danger')
        return redirect(url_for('rentals_all'))


@app.route('/owner/logout', methods=['POST'])
def logout_owner():
    session.clear()
    return redirect(url_for('admin'))


@app.route('/customer/logout', methods=['POST'])
def logout_customer():
    session.clear()
    return redirect(url_for('main'))


# debug mode
if __name__ == "__main__":
    app.run(debug=True)
