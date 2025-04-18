# Sends RPCs to a soia service.
# See start_service.py for how to start one.
#
# Run:
#   npm run call-service
# or:
#   npm run build
#   python call_service.py
from soiagen import service, user

import soia

if __name__ == "__main__":
    service_client = soia.ServiceClient("http://localhost:8787/myapi")

    print()
    print("About to add 2 users: John Doe and Tarzan")

    service_client.invoke_remote(
        service.AddUser,
        service.AddUserRequest(user=user.User(user_id=42, name="John Doe")),
    )

    res_headers: list[tuple[str, str]] = []
    service_client.invoke_remote(
        service.AddUser,
        service.AddUserRequest(user=user.TARZAN),
        {"X-Foo": "hi"},
        res_headers=res_headers,
    )

    # How to get headers from the response:
    x_bar_header = dict(res_headers).get("X-Bar")
    print(f"Value of X-Bar header: {x_bar_header}")

    print("Done")

    found_user = service_client.invoke_remote(
        service.GetUser,
        service.GetUserRequest(user_id=123),
    )

    print(f"Found user: {found_user}")
