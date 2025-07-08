# Starts a soia service on http://localhost:8787/?myapi
#
# Run with:
#   npm run start-service
# or:
#   npm run build
#   python start_service.py
#
# Run call_service.py to call this service from another process.

import urllib.parse

from flask import Flask, Response, request
from soiagen import service_soia, user_soia
from werkzeug.datastructures import Headers

import soia

app = Flask(__name__)


class ServiceImpl:
    def __init__(self):
        self._id_to_user = {}

    def get_user(
        self, request: service_soia.GetUserRequest
    ) -> service_soia.GetUserResponse:
        user_id = request.user_id
        user = self._id_to_user.get(user_id)
        return service_soia.GetUserResponse(user=user)

    def add_user(
        self,
        request: service_soia.AddUserRequest,
        req_headers: Headers,
        res_headers: Headers,
    ) -> service_soia.AddUserResponse:
        user = request.user
        if user.user_id == 0:
            raise ValueError("invalid user id")
        print(f"Adding user: {user}")
        self._id_to_user[user.user_id] = user
        res_headers["X-Bar"] = req_headers.get("X-Foo", "").upper()
        return service_soia.AddUserResponse()

    _id_to_user: dict[int, user_soia.User]


service_impl = ServiceImpl()

soia_service = soia.Service[Headers, Headers]()
soia_service.add_method(service_soia.AddUser, service_impl.add_user)
soia_service.add_method(service_soia.GetUser, service_impl.get_user)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/myapi", methods=["GET", "POST"])
def myapi():
    if request.method == "POST":
        req_body = request.get_data(as_text=True)
    else:
        req_body = urllib.parse.unquote(request.query_string.decode("utf-8"))
    req_headers = request.headers
    res_headers = Headers()
    raw_response = soia_service.handle_request(req_body, req_headers, res_headers)
    return Response(
        raw_response.data,
        status=raw_response.status_code,
        content_type=raw_response.content_type,
        headers=res_headers,
    )


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=int("8787"))
