def validate_limit(value, default=5, min_val=1, max_val=50):
    try:
        limit = int(value)
        if limit < min_val:
            return min_val
        elif limit > max_val:
            return max_val
        return limit
    except (ValueError, TypeError):
        return default

def validate_username(username):
    import re
    if not isinstance(username, str):
        return False
    return bool(re.match(r"^[0-9a-z]{3,32}$", username))

def validate_password(password):
    return isinstance(password, str) and len(password) > 0

def validate_gender(gender):
    return gender in (0, 1, 2)

def validate_tags(tags):
    if not isinstance(tags, dict):
        return False
    for value in tags.values():
        if value not in (0, 1):
            return False
    return True
