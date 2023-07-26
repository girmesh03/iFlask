from settings.configuration import Configuration
from iFlask_app.model import Model
from iFlask_app.view import View
import phonenumbers
import requests
import re

url = "http://192.168.43.192:5000/api/user"


class Controller:
    """Controller class to manage interactions between the Model and View.

    This class handles user interactions with the GUI,
    processes user input, validates data,
    and communicates with the Model to perform
    database operations. It also updates the View
    to display relevant information and messages to the user.

    Attributes:
        model (Model): An instance of the Model class representing
        the database operations.
        view (View): An instance of the View class representing
        the graphical user interface.
        config (Configuration): An instance of the Configuration
        class to manage configuration settings.
    """

    def __init__(self) -> None:
        """Initializes the Controller class."""
        self.model = Model()
        self.view = View(self)

        self.view.bind_enroll_user_task(self.enroll_user)
        self.view.bind_delete_user_task(self.delete_user)
        self.view.bind_update_user_task(self.update_user)
        self.view.bind_generate_report_task(self.generate_report)

        self.config = Configuration('settings/config.ini')

    def admin(self, option):
        """Handles administrative options, such as login, logout,
        and adding an admin user."""

        # get the current user
        current_user = self.config.get_value('User', 'current_user')
        if current_user == 'staff' and option == 'Login':
            self.view.admin_login_window(option)
            return

        if option == 'Logout' and current_user == 'admin':
            self.config.set_value('User', 'current_user', 'staff')
            self.config.save_changes()
            return

        if current_user == 'admin' and option == 'Add Admin User':
            self.view.admin_login_window(option)
        elif current_user == 'staff' and option == 'Add Admin User':
            self.view.display_message(
                'You are not authorized to perform this operation')
            return

    def admin_user(self, option, **kwargs):
        """Manages admin user-related operations, such as login and
        adding an admin user."""
        admin_dict = {}
        admin_dict['first_name'] = kwargs.get('first_name')
        admin_dict['last_name'] = kwargs.get('last_name')
        admin_dict['email'] = kwargs.get('email')
        admin_dict['password'] = kwargs.get('password')

        if option == 'Login':
            # get user from database
            email = kwargs.get('email')
            user = self.model.get_user_by_email(email)
            if user:
                self.save_admin_changes(
                    admin_dict['email'], admin_dict['password'])
                return True
            else:
                return False
        if option == 'Add Admin User':
            # add user to database
            user = self.model.add_admin(**admin_dict)
            if not user:
                return False

    def save_admin_changes(self, email, password):
        """Saves the admin user details to the configuration file
        after login."""

        self.config.set_value('Admin', 'email', email)
        self.config.set_value('Admin', 'password', password)
        self.config.set_value('User', 'current_user', 'admin')
        self.config.save_changes()

    def reset_default_config(self):
        """Resets the configuration file to its default settings."""
        self.config.set_value('User', 'current_user', 'staff')

        self.config.save_changes()

    def enroll_user(self, event=None):
        """Adds a new user to the database and communicates
        with the Flask API for enrollment."""

        user_inputs = self.view.get_user_entry_fields()
        is_valid = self.validate_user_inputs(**user_inputs)
        if is_valid is not None:
            self.view.display_message(is_valid)
            return

        # Clear entry fields
        self.view.clear_entry_fields()

        # Add user to database and return the user object
        new_user = self.model.add_user(**user_inputs)

        payload = {"user_id": new_user.id, "operation": "enroll"}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            # Add user to treeview
            self.view.add_user_to_treeview(new_user, update=False)
            # Display message to user
            self.view.display_message(
                "User enrolled successfully", new_user.id)
        else:
            # delete from database
            self.model.delete_user(new_user)
            # Display error message
            self.view.display_message(
                "Failed to enroll user", new_user.id)

    def delete_user(self, event=None):
        """Deletes a user from the database and communicates
        with the Flask API for deletion."""

        current_user = self.config.get_value('User', 'current_user')
        if current_user != 'admin':
            self.view.display_message(
                "You are not authorized to perform this operation")
            return
        # Get selected user from treeview
        selected_user = self.view.get_selected_user()
        print(selected_user.first_name)

        if selected_user is None:
            return

        # Clear entry fields
        self.view.clear_entry_fields()

        # send delete post request to Flask API
        payload = {"user_id": selected_user.id, "operation": "delete",
                   "first_name": selected_user.first_name}
        response = requests.delete(url, json=payload)

        if response.status_code == 200:
            # Delete user from database
            self.model.delete_user(selected_user)
            # Delete user from treeview
            self.view.delete_user_from_treeview()
            # Display message to user
            self.view.display_message(
                "User deleted successfully", selected_user.id)
        else:
            self.view.display_message(
                "Failed to delete user", selected_user.id)

    def update_user(self, event=None) -> None:
        """Updates a user's information in the database
        and reflects the changes in the View."""

        current_user = self.config.get_value('User', 'current_user')
        if current_user != 'admin':
            self.view.display_message(
                "You are not authorized to perform this operation")
            return
        # Get selected user from treeview
        selected_user = self.view.get_selected_user()
        if selected_user is None:
            self.view.display_message("Please select a user to update.")
            return

        # Get user inputs from entry fields
        user_inputs = self.view.get_user_entry_fields()
        for key, value in user_inputs.items():
            if key == 'country_code':
                user_inputs[key] = int(value.lstrip('+'))
            if key == 'phone_number':
                if len(value) == 9:
                    value = '0' + value
                user_inputs[key] = int(value)

        user_dict = selected_user.__dict__.copy()
        if '_sa_instance_state' in user_dict:
            user_dict.pop('_sa_instance_state', None)

        # Flag to track if any changes have been made
        changes_made = False

        # Iterate over the keys in user_inputs and compare the values
        for key in user_inputs:
            if user_inputs[key] != user_dict.get(key) and user_dict.get(key):
                print(key, type(user_inputs[key]), type(user_dict.get(key)))
                changes_made = True
                break

        if changes_made:
            # Update user in database
            self.model.update_user(selected_user, **user_inputs)

            # Update user in treeview
            self.view.update_user_treeview(selected_user.id)

            # Display message to user
            self.view.display_message(
                "User updated successfully", selected_user.id)
        else:
            # Display message to user
            self.view.display_message(
                "No changes in the entry fields. Skipping update.")

        # No changes in the entry fields
        self.view.clear_entry_fields()

    def generate_report(self, event=None):
        """Generates a report of all the users in the database."""
        all_users = self.model.get_all_users()
        self.view.generate_report(all_users)

    def validate_admin_inputs(self, option, **kwargs):
        """Validates the admin user input fields."""

        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')

        if not self.email or not self.password:
            # Please fill in all the required fields.
            return "Please fill in all the required fields"

        # Valid format for email: if not valid
        e_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        self.email_pattern = e_pattern
        if not re.match(self.email_pattern, self.email):
            # self.view.display_message("Invalid email format.")
            return "Please enter a valid email address"

        # Valid format for password: if not valid
        p_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{4,}$"
        self.password_pattern = p_pattern
        if not re.match(self.password_pattern, self.password):
            # Invalid password format.
            message = '''Password must contain at least 4 characters,
            1 uppercase letter, 1 lowercase letter and 1 number.'''
            return message

        # Maximum Length Validation
        max_length = 50  # Define the maximum length for fields if necessary
        if option == 'Add Admin User':
            if len(kwargs['first_name']) > max_length or \
                    len(kwargs['last_name']) > max_length:
                return "Name fields exceed the maximum length."
        if len(kwargs['email']) > max_length:
            return "Email field exceeds the maximum length."
        if len(kwargs['password']) > max_length:
            return "Password field exceeds the maximum length."

        return None

    def validate_user_inputs(self, **kwargs):
        """Validates the user input fields."""
        # Required Field Validation
        defalut_fields = ['First Name', 'Last Name',
                          'Email', 'Country Code', 'Phone Number',
                          'Select Gender', 'Membership Type']

        # Check if all required fields doesn't match the default fields
        for field in kwargs.values():
            if field in defalut_fields:
                return "Please fill in all the required fields."

        # Check the country code and phone number is valid
        country_code = kwargs['country_code']
        phone_number = kwargs['phone_number']

        try:
            # Format the phone number to international format
            formatted_number = f"+{country_code.lstrip('+')}{phone_number}"
            parsed_number = phonenumbers.parse(formatted_number, None)

            if not phonenumbers.is_valid_number(parsed_number):
                return "Invalid phone number."

            # Check if the parsed number belongs to the selected country code
            if parsed_number.country_code != int(country_code.lstrip('+')):
                return "Phone number does not match the selected country code."

        except phonenumbers.phonenumberutil.NumberParseException:
            return "Invalid phone number format."

        # Assuming a 10-digit phone number format
        phone_pattern = r"^[0-9]{10}$"
        if not re.match(phone_pattern, phone_number):
            return "Invalid phone number format."

        # Valid Characters Validation for first_name and last_name
        name_pattern = r"^[A-Za-z\s]+$"
        if not re.match(name_pattern, kwargs['first_name']) or \
                not re.match(name_pattern, kwargs['last_name']):
            return "Invalid characters in the name fields."

        # Valid format for email
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, kwargs['email']):
            return "Invalid email format."

        # Maximum Length Validation
        max_length = 50  # Define the maximum length for fields if necessary
        if len(kwargs['first_name']) > max_length or \
                len(kwargs['last_name']) > max_length:
            return "Name fields exceed the maximum length."
        if len(kwargs['email']) > max_length:
            return "Email field exceeds the maximum length."

        # Check if phone number already exists
        does_user_exist = self.model.get_user_by_phone_number(phone_number)
        if does_user_exist:
            return "Phone number already exists."

        # If all validations pass, return None to indicate no errors
        return None

    def reload(self):
        """Reloads the treeview with updated user data."""
        # reload treeview
        users = self.model.get_all_users()
        if not users:
            return

        # print(users)
        for user in users:
            self.view.add_user_to_treeview(user)
        # configure treeview
        self.view.configure_treeview()

    def get_user_by_id(self, user_id):
        """Retrieves a user object from the database based on
        the user_id."""

        return self.model.get_user_by_id(user_id)

    def get_all_users(self):
        """Retrieves all users from the database."""
        return self.model.get_all_users()

    def run(self) -> None:
        """Runs the Controller class."""
        self.view.mainloop()
