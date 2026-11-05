import uuid

import ldap


def ldap_login(username: str, password: str) -> bool:
    if not username or not password:
        return False
    conn = ldap.initialize("ldap://localhost:389")
    try:
        conn.simple_bind_s("cn={0},ou=users,dc=syncloud,dc=org".format(username), password)
    except ldap.INVALID_CREDENTIALS:
        print("{0} not authenticated".format(username), flush=True)
        return False
    except Exception as e:
        print("{0} not authenticated, error: {1}".format(username, str(e)), flush=True)
        return False
    finally:
        conn.unbind()
    print("{0} authenticated".format(username), flush=True)
    from . import add_user, get_user_details
    from .const import ROLE_ADMIN

    if not get_user_details(username):
        try:
            add_user(name=username, password=uuid.uuid4().hex, role=ROLE_ADMIN)
        except ValueError as e:
            print("Error adding user: {0}".format(e), flush=True)
            return False
    return True
