from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///data/database.db')


class User(Base):
    """
    Represents the 'users' table in the database.

    Attributes:
        id (int): Primary key for the user.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        email (str): Email address of the user.
        country_code (int): Country code for the
        user's phone number.
        phone_number (int): Phone number of the user.
        gender (str): Gender of the user.
        last_check_in (DateTime): Date and time of the user's
        last check-in (default is current UTC time).
        membership_type (str): Type of membership for the user.
        next_payment (DateTime): Date and time of the
        next payment (default is current UTC time).
        remaining_days (int): Number of remaining days
        for the membership.
        created_at (DateTime): Date and time when the user was
        created (default is current UTC time).
        updated_at (DateTime): Date and time when the user
        was last updated (default is current UTC time,
        updated automatically).

    Methods:
        __repr__: Returns a string representation of the User object.

    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    country_code = Column(Integer, nullable=False)
    phone_number = Column(Integer, nullable=False, unique=True)
    gender = Column(String(10), nullable=False)
    last_check_in = Column(DateTime, default=datetime.utcnow)
    membership_type = Column(String(50), nullable=False)
    next_payment = Column(DateTime, default=datetime.utcnow)
    remaining_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        """
        Returns a string representation of the User object.

        Returns:
            str: String representation of the User object.
        """
        return "[{}] ({}) {}".format(
            self.__tablename__, self.id, self.__dict__)


class Admin(Base):
    """
    Represents the 'admins' table in the database.

    Attributes:
        id (int): Primary key for the admin.
        first_name (str): First name of the admin.
        last_name (str): Last name of the admin.
        email (str): Email address of the admin (unique).
        password (str): Password of the admin.

    Methods:
        __init__: Initializes a new Admin object with provided kwargs.
        __repr__: Returns a string representation of the Admin object.

    """
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(150), nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes a new Admin object with provided kwargs.

        Args:
            **kwargs: Keyword arguments containing
            admin details (first_name, last_name, email, password).
        """
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')

    def __repr__(self):
        """
        Returns a string representation of the Admin object.

        Returns:
            str: String representation of the Admin object.
        """
        return "[{}] ({}) {}".format(
            self.__tablename__, self.id, self.__dict__)
