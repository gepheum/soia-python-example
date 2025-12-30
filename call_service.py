# Sends RPCs to a skir service.
# See start_service.py for how to start one.
#
# Run with:
#   python call_service.py
import skir

from skirout import service_skir, user_skir

if __name__ == "__main__":
    service_client = skir.ServiceClient("http://localhost:8787/myapi")

    print()
    print("About to add 2 users: John Doe and Tarzan")

    service_client.invoke_remote(
        service_skir.AddUser,
        service_skir.AddUserRequest(
            user=user_skir.User.partial(user_id=42, name="John Doe")
        ),
    )

    res_headers: list[tuple[str, str]] = []
    service_client.invoke_remote(
        service_skir.AddUser,
        service_skir.AddUserRequest(user=user_skir.TARZAN),
        {"X-Foo": "hi"},
        res_headers=res_headers,
    )

    # How to get headers from the response:
    x_bar_header = dict(res_headers).get("X-Bar")
    print(f"Value of X-Bar header: {x_bar_header}")

    print("Done")

    found_user = service_client.invoke_remote(
        service_skir.GetUser,
        service_skir.GetUserRequest(user_id=123),
    )

    print(f"Found user: {found_user}")
