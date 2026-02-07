from booot.enums import Role


def has_role(user_role: str, allowed: set[Role]) -> bool:
    try:
        role = Role(user_role)
    except Exception:
        return False
    return role in allowed
