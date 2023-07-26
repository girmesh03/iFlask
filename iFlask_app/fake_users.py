"""This script generates fake user data using the Faker library."""

from faker import Faker
from datetime import datetime
import phonenumbers

fake = Faker()

fake_user_list = []

while len(fake_user_list) < 10:
    # Generate random user data using the Faker library
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    country_code = fake.country_calling_code()

    phone_number = fake.random_int(
        min=1000000000, max=9999999999)

    gender = fake.random_element(elements=('Male', 'Female'))

    last_check_in = fake.date_time_this_month(
        before_now=True, after_now=False)

    membership_type = fake.random_element(
        elements=('Member', 'Not Member'))

    next_payment = fake.date_time_this_decade(
        before_now=False, after_now=True)

    remaining_days = fake.random_int(min=30, max=31)

    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()

    full_phone_number = f"+{country_code} {phone_number}"

    # Exclude phone numbers in the format "+882 16 xxxxxxxxxx"
    if country_code == '+882 16':
        continue

    try:
        # Validate the phone number using phonenumbers library
        parsed_number = phonenumbers.parse(full_phone_number, None)
        if phonenumbers.is_valid_number(parsed_number):
            # Create a dictionary representing the fake user data
            user_dict = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'country_code': country_code,
                'phone_number': phone_number,
                'gender': gender,
                'last_check_in': last_check_in,
                'membership_type': membership_type,
                'next_payment': next_payment,
                'remaining_days': remaining_days,
                'created_at': created_at,
                'updated_at': updated_at
            }
            # Exclude repetitions in the dictionary and add
            #  the fake user data to the list
            if user_dict not in fake_user_list:
                fake_user_list.append(user_dict)
    except phonenumbers.phonenumberutil.NumberParseException:
        # Ignore invalid phone numbers that couldn't be parsed
        pass
