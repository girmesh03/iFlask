"""RESTful API for the iFlask application."""

from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime
from iFlask_app.model import Model
import requests

app = Flask(__name__)
api = Api(app)

ESP32_IP = "192.168.43.63"


class UserController(Resource):
    """A RESTful API for the iFlask application,
    which exposes the /api/user endpoint, and a bridge
    between the esp32 and iFlask controller class."""

    def __init__(self):
        """Initialize the UserController class."""
        self.model = Model()

    def get(self):
        """GET request handler for the /api/user endpoint."""
        return {'status': 'success'}, 200

    def post(self):
        """POST request handler for the /api/user endpoint."""
        data = request.get_json()
        user_id = data['user_id']
        operation = data['operation']

        if operation == "enroll":
            url = f"http://{ESP32_IP}/enroll_user"
            payload = {"user_id": user_id, "operation": operation}
            response = requests.get(url, params=payload)

            if response.status_code == 200:
                return {'message': 'User enrolled successfully.'}, 200
            else:
                return {'message': 'Failed to enroll user.'}, 500
        elif operation == 'checkin':

            checkedin_user = self.model.get_user_by_id(user_id)
            if checkedin_user:
                now = datetime.utcnow()
                if ((checkedin_user.last_check_in
                     ).date()) != now.date():
                    checkedin_user = self.model.get_user_update(
                        checkedin_user.id)
                return {'user_id': str(user_id),
                        'first_name': str(checkedin_user.first_name)}, 200
            else:
                return {'message': 'User not found.'}, 404
        else:
            return {'message': 'Invalid operation.'}, 400

    def delete(self):
        """DELETE request handler for the /api/user endpoint."""
        data = request.get_json()
        user_id = data['user_id']
        operation = data['operation']
        first_name = data['first_name']

        if operation == "delete":
            # Send the delete request to ESP32
            url = f"http://{ESP32_IP}/delete_user"
            payload = {"user_id": user_id,
                       "operation": operation,
                       "first_name": first_name}
            response = requests.get(url, params=payload)

            if response.status_code == 200:
                return {'message': 'User deleted successfully.'}, 200
            else:
                return {'message': 'Failed to delete user.'}, 500
        else:
            return {'message': 'Invalid operation.'}, 400


api.add_resource(UserController, '/api/user')

if __name__ == "__main__":
    """Run the iFlask Api server."""
    app.run(host='0.0.0.0', port=5000)
