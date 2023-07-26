"""This module contains the Model class."""

from sqlalchemy.orm import sessionmaker
from iFlask_app.user_model import User, Admin, engine, Base
from settings.configuration import Configuration
from datetime import datetime


class Model:
    """The Model class is responsible for interacting with the database."""

    def __init__(self) -> None:
        """Initialize the Model class."""
        self.config = Configuration('settings/config.ini')
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.create_database()
        self.add_fake_users()
        self.create_default_admin()

    def create_database(self):
        """Create the database if it doesn't exist."""
        is_db_created = self.config.get_value('Database', 'is_created')
        if is_db_created == 'False':
            Base.metadata.create_all(engine)
            self.config.set_value('Database', 'is_created', 'True')
            self.config.save_changes()

    def add_fake_users(self):
        """Add fake users to the database if not already added."""
        self.fake_data_created = self.config.get_value(
            'FakeData', 'is_created')
        if self.fake_data_created == 'False':
            from iFlask_app.fake_users import fake_user_list
            for user in fake_user_list:
                if user['country_code'] == '+882 16':
                    user['country_code'] = '+882'
                self.add_user(**user)
            self.config.set_value('FakeData', 'is_created', 'True')
            self.config.save_changes()

    def create_default_admin(self):
        """Create a default admin user if not already created."""
        is_admin_created = self.config.get_value('Admin', 'admin_created')
        if is_admin_created == 'False':
            admin_dict = {}
            admin_dict['first_name'] = 'admin'
            admin_dict['last_name'] = 'admin'
            admin_dict['email'] = 'admin@gmail.com'
            admin_dict['password'] = 'Admin1234'

            admin = self.add_admin(**admin_dict)
            if admin:
                self.config.set_value('Admin', 'admin_created', 'True')
                self.config.save_changes()
            else:
                pass

    def get_all_users(self):
        """Retrieve all users from the database."""
        return self.session.query(User).all()

    def add_user(self, **kwargs):
        """Create a new user in the database."""
        user = User(**kwargs)
        self.session.add(user)
        self.session.commit()
        return user

    def add_admin(self, **kwargs):
        """Create a new admin user in the database."""
        admin = Admin(**kwargs)
        self.session.add(admin)
        self.session.commit()
        return admin

    def delete_user(self, user):
        """Delete a user from the database."""
        self.session.delete(user)
        self.session.commit()

    def update_user(self, user, **kwargs):
        """Update a user in the database."""
        self.session.query(User).filter_by(id=user.id).update(kwargs)
        self.session.commit()

    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID."""
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_phone_number(self, phone_number):
        """Retrieve a user by their phone number."""
        return self.session.query(User).filter_by(
            phone_number=phone_number).first()

    def get_number_of_users(self):
        """Get the number of users in the database."""
        return self.session.query(User).count()

    def get_user_update(self, user_id):
        """Update a user last check in,
        remaining days, and return the user object or None."""
        user = self.session.query(User).filter_by(id=user_id).first()
        if user and user.remaining_days > 0:
            user_dict = {}
            user_dict['last_check_in'] = datetime.utcnow()
            user_dict['remaining_days'] = user.remaining_days - 1
            self.update_user(user, **user_dict)
            return user
        else:
            return None

    def get_admin_user_by_email(self, email):
        """Retrieve an admin user by their email."""
        return self.session.query(Admin).filter_by(email=email).first()
