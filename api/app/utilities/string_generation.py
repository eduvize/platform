import secrets
import string


def generate_random_string(length: int):
    """
    Generates a random string of a given length

    Args:
        length (int): The length of the string to generate

    Returns:
        _type_: The generated string
    """
    
    characters = string.ascii_uppercase + string.digits
    verification_code = ''.join(secrets.choice(characters) for i in range(length))
    return verification_code