from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///database.db')


class User(Base):
    """Represents the 'users' table in the database."""
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
        """Returns a string representation of the User object."""
        return "[{}] ({}) {}".format(
            self.__tablename__, self.id, self.__dict__)


class Admin(Base):
    """Represents the 'admins' table in the database."""
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(150), nullable=False)

    def __repr__(self):
        """Returns a string representation of the Admin object."""
        return "[{}] ({}) {}".format(
            self.__tablename__, self.id, self.__dict__)
