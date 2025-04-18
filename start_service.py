# Starts a soia service on http://localhost:8787/?myapi
#
# Run with:
#   npm run server
# or:
#   npm run build
#   python start_service.py
#
# Run call_service.py to call this service from another process.

import urllib.parse

from flask import Flask, Response, request
from soiagen import service, user

import soia

app = Flask(__name__)


class ServiceImpl:
    def __init__(self):
        self._id_to_user = {}

    def get_user(self, request: service.GetUserRequest) -> service.GetUserResponse:
        user_id = request.user_id
        user = self._id_to_user.get(user_id)
        return service.GetUserResponse(user=user)

    def add_user(
        self,
        request: service.AddUserRequest,
        req_headers: soia.RequestHeaders,
        res_headers: soia.ResponseHeaders,
    ) -> service.AddUserResponse:
        user = request.user
        if user.user_id == 0:
            raise ValueError("invalid user id")
        self._id_to_user[user.user_id] = user
        res_headers["X-Bar"] = req_headers.get("X-Foo", "").upper()
        return service.AddUserResponse()

    _id_to_user: dict[int, user.User]


service_impl = ServiceImpl()

soia_service = soia.Service()
soia_service.add_method(service.AddUser, service_impl.add_user)
soia_service.add_method(service.GetUser, service_impl.get_user)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/myapi", methods=["GET", "POST"])
def myapi():
    if request.method == "POST":
        req_body = request.get_data(as_text=True)
    else:
        req_body = urllib.parse.unquote(request.query_string.decode("utf-8"))
    req_headers = dict(request.headers)
    res_headers: dict[str, str] = {}
    raw_response = soia_service.handle_request(req_body, req_headers, res_headers)
    return Response(
        raw_response.data,
        status=raw_response.status_code,
        content_type=raw_response.content_type,
        headers=res_headers,
    )


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=int("8787"))
