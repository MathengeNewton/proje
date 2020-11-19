from app import db,bcrypt

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone_number = db.Column(db.String(30), nullable=False, unique=True)
    role = db.Column(db.String(),nullable=False)
    password = db.Column(db.String(80), nullable=False)

    # insert new user class

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # check if email is in use
    @classmethod
    def check_users_exists(cls, email):
        customer = cls.query.filter_by(email=email).first()
        if customer:
            return True
        else:
            return False

    @classmethod
    def validate_password(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return True
        else:
            return False

    @classmethod
    def get_user_role(cls, id):
        return cls.query.filter_by(id=id).first().role

    @classmethod
    def get_user_id(cls, email):
        return cls.query.filter_by(email=email).first().id

    @classmethod
    def get_user_by_email(cls, mail):
        user = cls.query.filter_by(email=mail).all()
        if user:
            return user
        else:
            print('user:',user)
            return False

    @classmethod
    def get_user_by_id(cls, id):
        user = cls.query.filter_by(id=id)
        return user


    @classmethod
    def get_user_id_by_email_role(cls,email,role):
        user = cls.query.filter_by(email = email).filter_by(role = role).first()
        if user:
            return user.id
        else:
            return False

    @classmethod
    def get_user_details_by_id(cls, id):
        return cls.query.filter_by(id = id)

class Property(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    img = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(), nullable=False, default='vacant')
    category = db.Column(db.String(),nullable=False)
    house_type = db.Column(db.String(),nullable=False)
    owner = db.Column(db.Integer,nullable = False)

    # insert rental

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # fetch all rentals
    @classmethod
    def fetch_all(cls):
        return cls.query.all()

    # fetch where status is 1
    @classmethod
    def fetch_by_status_occupied(cls):
        return cls.query.filter_by(status=u'vacant').filter_by(category = "rental").all()
    
    @classmethod
    def fetch_vacant_sales_property(cls):
        return cls.query.filter_by(status='vacant').filter_by(category = "sale").all()

    # get rental by id
    @classmethod
    def get_rental_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def get_rental_detail_by_id(cls, id):
        return cls.query.filter_by(id=id)

    @classmethod
    def get_rental_owner_by_id(cls, id):
        return cls.query.filter_by(id=id).first().owner

    @classmethod
    def get_rental_price(cls, id):
        return cls.query.filter_by(id=id).first().price
    # update status
        # update rental

    @classmethod
    def update_rental_details(cls,id,location,description,price,status):
        rental = cls.query.filter_by(id = id).first()
        if rental:
            try:
                rental.location = location
                rental.description = description
                rental.price = price
                rental.status = status
                db.session.commit()
                return True
            except:
                return False
        else:
            return False


    @classmethod
    def update_rental_by_id(cls, id):
        rental = cls.query.filter_by(id=id).first()

        if rental:
            status = rental.status
            if status:
                if status == 'booked':
                    newstatus = 'vacant'
                    rental.status = newstatus
                    db.session.commit()
                    return True
                else:
                    newstatus = 'booked'
                    rental.status = newstatus
                    db.session.commit()
                    return True
            else:
                return False
        else:
            return False

    # delete rental by id
    @classmethod
    def delete_by_id(cls, id):
        rental = cls.query.filter_by(id=id)
        if rental.first():
            rental.delete()
            db.session.commit()
            return True
        else:
            return False


class Bookings(db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    rental_id = db.Column(db.Integer)
    booking_date = db.Column(db.Date)
    customer_email = db.Column(db.String)


    def insert_record(self):
        db.session.add(self)
        db.session.commit()


    @classmethod
    def fetch_all(cls):
        return cls.query.all()

   
   
    @classmethod
    def get_booking_id_by_rental_id(cls, id):
        return cls.query.filter_by(rental_id=id).first().id

    @classmethod
    def get_booking_by_id(cls, fid):
        tw =  cls.query.filter_by(id=fid).first()
        if tw:

            return tw
        else:
            return False


    @classmethod
    def delete_all(cls):
        booked = cls.query.delete()
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        booking = cls.query.filter_by(id=id)
        if booking.first():
            booking.delete()
            db.session.commit()
            return True
        else:
            return False


class Wallet(db.Model):
    __tablename__='wallet'
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer,unique = True)
    balance = db.Column(db.Integer,default = 0)

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def record_by_id(cls,id):
        record = cls.query.filter_by(id = id).first()
        return record

    @classmethod
    def get_record_by_client(cls,client):
        record = cls.query.filter_by(client_id = client)
        return record
    @classmethod
    def get_client_balance(cls,client):
        record = cls.query.filter_by(client_id=client).first().balance
        if record:
            return record
        else:
            return False

    @classmethod
    def increase_balance_by_client_id(cls,id,amount):
        record = cls.query.filter_by(client_id = id).first()
        if record:
            record.balance = int(record.balance) + int(amount)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def reduce_balance_by_client_id(cls,id,amount):
        record = cls.query.filter_by(client_id = id).first()
        if record:
            record.balance = int(record.balance) - int(amount)
            db.session.commit()
            return True
        else:
            return False



class Payments(db.Model):
    __tablename__='payments'
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    to_= db.Column(db.Integer)
    from_ =  db.Column(db.Integer)
    amount = db.Column(db.Integer,default = 0)
    date = db.Column(db.Date,nullable = False)



    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def owner_payments(cls,id):
        payments = cls.query.all()
        return payments

    @classmethod
    def customer_payments(cls,id):
        payments = cls.query.filter_by(to_ = id).all()
        return payments

    

