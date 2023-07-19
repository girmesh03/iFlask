from sqlalchemy.orm import sessionmaker
from .user_model import User, Admin, engine, Base
from settings.configuration import Configuration
from datetime import datetime


class Model:
    def __init__(self) -> None:
        """Initialize the Model class."""
        self.config = Configuration('app/config.ini')
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.create_database()
        self.add_fake_users()

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
            from .fake_users import fake_user_list
            for user in fake_user_list:
                if user['country_code'] == '+882 16':
                    user['country_code'] = '+882'
                self.add_user(**user)
            self.config.set_value('FakeData', 'is_created', 'True')
            self.config.save_changes()

    def get_all_users(self):
        """Retrieve all users from the database."""
        return self.session.query(User).all()

    def add_user(self, **kwargs):
        """
        Create a new user.

        Args:
            **kwargs: Keyword arguments representing user data.

        Returns:
            User: The newly created user object.
        """
        user = User(**kwargs)
        self.session.add(user)
        self.session.commit()
        return user

    def add_admin(self, **kwargs):
        """
        Create a new admin user.

        Args:
            **kwargs: Keyword arguments representing admin user data.

        Returns:
            Admin: The newly created admin user object.
        """
        admin = Admin(**kwargs)
        self.session.add(admin)
        self.session.commit()
        return admin

    def delete_user(self, user):
        """
        Delete a user from the database.

        Args:
            user (User): The user object to be deleted.
        """
        self.session.delete(user)
        self.session.commit()

    def update_user(self, user, **kwargs):
        """
        Update a user in the database.

        Args:
            user (User): The user object to be updated.
            **kwargs: Keyword arguments representing user data to be updated.
        """
        self.session.query(User).filter_by(id=user.id).update(kwargs)
        self.session.commit()

    def get_user_by_id(self, user_id):
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The user object matching the ID, or None if not found.
        """
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_phone_number(self, phone_number):
        """
        Retrieve a user by their phone number.

        Args:
            phone_number (str): The phone number of the user.

        Returns:
            User: The user object matching the phone number,
            or None if not found.
        """
        return self.session.query(User).filter_by(phone_number=phone_number).first()

    def get_number_of_users(self):
        """
        Get the total number of users in the database.

        Returns:
            int: The number of users.
        """
        return self.session.query(User).count()

    def get_user_update(self, user_id):
        """
        Get the user object with an update.

        This method retrieves the user from the database and
        performs an update if the user's remaining days are greater than 0.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The updated user object, or
            None if the user doesn't require an update.
        """
        user = self.session.query(User).filter_by(id=user_id).first()
        if user and user.remaining_days > 0:
            user_dict = {}
            user_dict['last_check_in'] = datetime.utcnow()
            user_dict['remaining_days'] = user.remaining_days - 1
            self.update_user(user, **user_dict)
            return user
        else:
            return None

    def get_user_by_email(self, email):
        """
        Retrieve an admin user by their email.

        Args:
            email (str): The email of the admin user.

        Returns:
            Admin: The admin user object matching the email,
            or None if not found.
        """
        return self.session.query(Admin).filter_by(email=email).first()
