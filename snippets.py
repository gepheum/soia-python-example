# Code snippets showing how to use Python-generated data classes.
#
# Run with:
#   npm run snippets
# or:
#   npm run build
#   python snippets.py

from typing import Never

import soia.reflection

# Import the given symbols from the Python module generated from "user.soia"
from soiagen.user_soia import TARZAN, User, UserHistory, UserRegistry

import soia

# FROZEN STRUCT CLASSES

# For every struct S in the .soia file, soia generates a frozen/deeply immutable
# class 'S' and a mutable class 'S.Mutable'.

# To consruct a frozen/deeply immutable User, either call the partial() static
# factory method or the constructor.

john = User.partial(
    user_id=42,
    name="John Doe",
)

assert john.name == "John Doe"
assert john.user_id == 42
# Fields not specified in the call to partial() are set to their default values
assert john.pets == ()

# Static type checkers will raise an error if you try to modify a frozen struct:
# john.name = "John Smith"

# If you call the constructor, you have to specify all the fields.
jane = User(
    user_id=43,
    name="Jane Doe",
    quote="I am Jane.",
    pets=[
        User.Pet.partial(name="Fluffy"),
        User.Pet.partial(name="Fido"),
    ],
    subscription_status=User.SubscriptionStatus.PREMIUM,
)

# The list passed to the constructor or partial() is copied into a tuple to
# guarantee deep immutability.
assert isinstance(jane.pets, tuple)

assert User.DEFAULT == User.partial()

# MUTABLE STRUCT CLASSES

# User.Mutable is a mutable version of User.
lyla_mut = User.Mutable()
lyla_mut.user_id = 44
lyla_mut.name = "Lyla Doe"

# You can also set fields in the constructor.
joly_mut = User.Mutable(user_id=45)
joly_mut.name = "Joly Doe"

joly_history_mut = UserHistory.Mutable()
joly_history_mut.user = joly_mut
# ^ The right-hand side of the assignment can be either frozen or mutable.

# joly_history_mut.user.quote = "I am Joly."
# ^ Static error: quote is readonly because joly_history_mut.user may be frozen

# The mutable_user() property first checks if 'user' is already a mutable
# struct, and if so, returns it. Otherwise, it assigns to 'user' a mutable
# shallow copy of itself and returns it.
joly_history_mut.mutable_user.quote = "I am Joly."

# Similarly, mutable_pets() first checks if 'pets' is already a mutable array,
# and if so, returns it. Otherwise, it assigns to 'pets' a mutable shallow copy
# of itself and returns it.
lyla_mut.mutable_pets.append(User.Pet.partial(name="Cupcake"))
lyla_mut.mutable_pets.append(User.Pet.Mutable(name="Simba"))

# CONVERTING BETWEEN FROZEN AND MUTABLE

# to_mutable() does a shallow copy of the frozen struct, so it's cheap. All the
# properties of the copy hold a frozen value.
evil_jane_mut = jane.to_mutable()
evil_jane_mut.name = "Evil Jane"

# to_frozen() recursively copies the mutable values held by properties of the
# object. It's cheap if all the values are frozen, like in this example.
evil_jane: User = evil_jane_mut.to_frozen()

# You can also call replace() on the frozen struct.
evil_jane = evil_jane.replace(name="Evil Jane")
# Same as:
#   evil_jane_mut = evil_jane.to_mutable()
#   evil_jane_mut.name = "Evil Jane"
#   evil_jane = evil_jane_mut.to_frozen()

assert evil_jane.user_id == 43

# WRITING LOGIC AGNOSTIC OF MUTABILITY


# 'User.OrMutable' is a type alias for 'User | User.Mutable'.
def greet(user: User.OrMutable):
    print(f"Hello, ${user.name}")


greet(jane)
# Hello, Jane Doe
greet(lyla_mut)
# Hello, Lyla Doe

# MAKING ENUM VALUES

john_status = User.SubscriptionStatus.FREE
jane_status = User.SubscriptionStatus.PREMIUM

joly_status = User.SubscriptionStatus.UNKNOWN

# Use wrap_*() for data variants.
roni_status = User.SubscriptionStatus.wrap_trial(
    User.Trial(start_time=soia.Timestamp.from_unix_millis(1744974198000))
)

# CONDITIONS ON ENUMS

# Use e.kind == "CONSTANT_NAME" to check if the enum value is a constant.
assert john_status.kind == "FREE"
assert john_status.value is None

# Static type checkers will complain: "RED" not in the enum definition.
# assert jane_status.kind == "RED"

# Use "?" for UNKNOWN.
assert joly_status.kind == "?"

assert roni_status.kind == "trial"
assert isinstance(roni_status.value, User.Trial)


def get_subscription_info_text(status: User.SubscriptionStatus) -> str:
    # Use the union() getter for typesafe switches on enums.
    if status.union.kind == "?":
        return "Unknown subscription status"
    elif status.union.kind == "FREE":
        return "Free user"
    elif status.union.kind == "trial":
        # Here the compiler knows that the type of union.value is 'User.Trial'
        trial: User.Trial = status.union.value
        return f"On trial since {trial.start_time}"
    elif status.union.kind == "PREMIUM":
        return "Premium user"

    # Static type checkers will complain here if you missed a case.
    _: Never = status.union.kind
    raise AssertionError("Unreachable code")


# SERIALIZATION

# Serialize 'john' to dense JSON.

serializer = User.SERIALIZER

print(serializer.to_json(john))
# [42, 'John Doe']

assert isinstance(serializer.to_json(john), list)

# to_json_code() returns a string containing the JSON code.
# Same as calling json.dumps() on the result of to_json()
print(serializer.to_json_code(john))
# [42,"John Doe"]

# Serialize 'john' to readable JSON.
print(serializer.to_json_code(john, readable=True))
# {
#   "user_id": 42,
#   "name": "John Doe"
# }

# The dense JSON flavor is the flavor you should pick if you intend to
# deserialize the value in the future. Soia allows fields to be renamed, and
# because fields names are not part of the dense JSON, renaming a field does
# not prevent you from deserializing the value.
# You should pick the readable flavor mostly for debugging purposes.

# DESERIALIZATION

# Use from_json() and from_json_code() to deserialize.

assert john == serializer.from_json(serializer.to_json(john))

assert john == serializer.from_json_code(serializer.to_json_code(john))

# Also works with readable JSON.
assert john == serializer.from_json_code(  #
    serializer.to_json_code(john, readable=True)
)

# KEYED ARRAYS

user_registry = UserRegistry(users=[john, jane, lyla_mut])

# 'user_registry.users' is an instance of a subclass of tuple[User, ...] which
# has methods for finding items by key.

assert user_registry.users.find(42) == john
assert user_registry.users.find(100) is None

assert user_registry.users.find_or_default(42).name == "John Doe"
assert user_registry.users.find_or_default(100).name == ""

# find() and find_or_default() run in O(1) time.

# CONSTANTS

print(TARZAN)
# User(
#   user_id=123,
#   name='Tarzan',
#   quote='AAAAaAaAaAyAAAAaAaAaAyAAAAaAaAaA',
#   pets=[
#     User.Pet(
#       name='Cheeta',
#       height_in_meters=1.67,
#       picture='🐒',
#     ),
#   ],
#   subscription_status=User.SubscriptionStatus.wrap_trial(
#     User.Trial(
#       start_time=Timestamp(
#         unix_millis=1743592409000,
#         _formatted='2025-04-02T11:13:29Z',
#       ),
#     )
#   ),
# )

# REFLECTION

# Reflection allows you to inspect a soia type at runtime.

field_names: list[str] = []

user_type_descriptor = User.SERIALIZER.type_descriptor

# 'user_type_descriptor' has information about User and all the types it
# depends on.

print(user_type_descriptor.as_json_code())
# {
#   "type": {
#     "kind": "record",
#     "value": "user.soia:User"
#   },
#   "records": [
#     {
#       "kind": "struct",
#       "id": "user.soia:User",
#       "fields": [
#         {
#           "name": "user_id",
#           "type": {
#             "kind": "primitive",
#             "value": "int64"
#           },
#           "number": 0
#         },
#          ...
#         {
#           "name": "pets",
#           "type": {
#             "kind": "array",
#             "value": {
#               "item": {
#                 "kind": "record",
#                 "value": "user.soia:User.Pet"
#               }
#             }
#           },
#           "number": 3
#         },
#         ...
#       ]
#     },
#     {
#       "kind": "struct",
#       "id": "user.soia:User.Pet",
#       ...
#     },
#     ...
#   ]
# }

# A TypeDescriptor can be serialized and deserialized.
assert user_type_descriptor == soia.reflection.TypeDescriptor.from_json_code(
    user_type_descriptor.as_json_code()
)
