from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime
from iFlask_app.model import Model
import requests

app = Flask(__name__)
api = Api(app)

ESP32_IP = "192.168.43.63"


class UserController(Resource):
    """
    Represents the RESTful API endpoints for user-related operations.

    - GET: Returns a success status.
    - POST: Enrolls or checks in a user.
    - DELETE: Deletes a user.

    Endpoints:
    - /api/user
    """

    def get(self):
        """
        GET request handler for the /api/user endpoint.

        Returns:
            dict: Response containing a success status.

        HTTP Status Codes:
            - 200: Success.
        """
        return {'status': 'success'}, 200

    def post(self):
        """
        POST request handler for the /api/user endpoint.

        Expects a JSON payload containing 'user_id'
        and 'operation' fields.
        Performs the specified operation on the user.

        Returns:
            dict: Response containing a message
            indicating the operation result.

        HTTP Status Codes:
            - 200: Success.
            - 404: User not found.
            - 500: Internal server error.
            - 400: Invalid operation.
        """
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
            model = Model()
            checkedin_user = model.get_user_by_id(user_id)
            if checkedin_user:
                now = datetime.utcnow()
                if ((checkedin_user.last_check_in
                     ).date()) != now.date():
                    checkedin_user = model.get_user_update(
                        checkedin_user.id)
                return {'user_id': str(user_id),
                        'first_name': str(checkedin_user.first_name)}, 200
            else:
                return {'message': 'User not found.'}, 404
        else:
            return {'message': 'Invalid operation.'}, 400

    def delete(self):
        """
        DELETE request handler for the /api/user endpoint.

        Expects a JSON payload containing
        'user_id', 'operation',
        and 'first_name' fields.
        Deletes the specified user.

        Returns:
            dict: Response containing a message
            indicating the operation result.

        HTTP Status Codes:
            - 200: Success.
            - 500: Internal server error.
            - 400: Invalid operation.
        """
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
    app.run(host='0.0.0.0', port=5000)
