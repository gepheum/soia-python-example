from typing import Never

import soia.reflection

# Import the given symbols from the Python module generated from "user.soia"
from soiagen.user import TARZAN, User, UserHistory, UserRegistry

import soia

# FROZEN STRUCT CLASSES

# For every struct S in the .soia file, soia generates a frozen/deeply immutable
# class 'S' and a mutable class 'S.Mutable'.

# Consruct a frozen/deeply immutable User
john = User(
    user_id=42,
    name="John Doe",
)

assert john.name == "John Doe"
assert john.user_id == 42
# Fields not specified in the constructor are set to their default values
assert john.pets == ()

# Static type checkers will raise an error if you try to modify a frozen struct:
# john.name = "John Smith"

jane = User(
    user_id=43,
    name="Jane Doe",
    quote="I am Jane.",
    pets=[User.Pet(name="Fluffy"), User.Pet(name="Fido")],
    subscription_status=User.SubscriptionStatus.PREMIUM,
)

# The list passed to the constructor is copied into a tuple to guarantee deep
# immutability.
assert isinstance(jane.pets, tuple)

assert User.DEFAULT == User()

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
lyla_mut.mutable_pets.append(User.Pet(name="Cupcake"))
lyla_mut.mutable_pets.append(User.Pet.Mutable(name="Simba"))

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
#         {
#           "name": "name",
#           "type": {
#             "kind": "primitive",
#             "value": "string"
#           },
#           "number": 1
#         },
#         {
#           "name": "quote",
#           "type": {
#             "kind": "primitive",
#             "value": "string"
#           },
#           "number": 2
#         },
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
#         {
#           "name": "subscription_status",
#           "type": {
#             "kind": "record",
#             "value": "user.soia:User.SubscriptionStatus"
#           },
#           "number": 4
#         }
#       ]
#     },
#     {
#       "kind": "struct",
#       "id": "user.soia:User.Pet",
#       "fields": [
#         {
#           "name": "name",
#           "type": {
#             "kind": "primitive",
#             "value": "string"
#           },
#           "number": 0
#         },
#         {
#           "name": "height_in_meters",
#           "type": {
#             "kind": "primitive",
#             "value": "float32"
#           },
#           "number": 1
#         },
#         {
#           "name": "picture",
#           "type": {
#             "kind": "primitive",
#             "value": "string"
#           },
#           "number": 2
#         }
#       ]
#     },
#     {
#       "kind": "enum",
#       "id": "user.soia:User.SubscriptionStatus",
#       "fields": [
#         {
#           "name": "trial",
#           "type": {
#             "kind": "record",
#             "value": "user.soia:User.Trial"
#           },
#           "number": 2
#         }
#       ]
#     },
#     {
#       "kind": "struct",
#       "id": "user.soia:User.Trial",
#       "fields": [
#         {
#           "name": "start_time",
#           "type": {
#             "kind": "primitive",
#             "value": "timestamp"
#           },
#           "number": 0
#         }
#       ]
#     }
#   ]
# }

# A TypeDescriptor can be serialized and deserialized.
assert user_type_descriptor == soia.reflection.TypeDescriptor.from_json_code(
    user_type_descriptor.as_json_code()
)
