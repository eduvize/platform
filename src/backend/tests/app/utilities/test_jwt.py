import pytest
import jwt
from datetime import datetime, timedelta
from app.utilities.jwt import create_token, decode_token, InvalidJWTToken

SECRET = "supersecretkey"

@pytest.mark.parametrize("data, expiration_minutes", [
    ({"user_id": 123}, 5),
    ({"username": "testuser"}, 10),
])
def test_create_token(data, expiration_minutes):
    """
    Test the successful creation of a JWT token.
    
    Assertions:
    1. Ensure the token is created and is a non-empty string.
    2. Ensure the "exp" field is correctly set in the token payload.
    3. Ensure the token can be decoded successfully with the correct secret and algorithm.
    """
    token = create_token(data, SECRET, expiration_minutes)
    
    # Assert that the token is not empty
    assert isinstance(token, str)
    assert len(token) > 0  # 1
    
    # Decode the token to verify its contents
    decoded_data = jwt.decode(token, SECRET, algorithms=["HS256"])
    
    # Check that the "exp" field is present and valid
    assert "exp" in decoded_data  # 2
    expiration = datetime.utcfromtimestamp(decoded_data["exp"])
    assert expiration > datetime.utcnow()  # The expiration should be in the future
    
    # Ensure the decoded token contains the original data
    for key, value in data.items():
        assert decoded_data[key] == value  # 3

@pytest.mark.parametrize("token_data", [
    ({"user_id": 123}),
    ({"username": "testuser"}),
])
def test_decode_token_valid(token_data):
    """
    Test decoding a valid JWT token.

    Assertions:
    1. Ensure the token is decoded properly and the data matches the input.
    2. Ensure the decoded data contains the correct values.
    """
    # Create a valid token
    token = create_token(token_data, SECRET, expiration_minutes=5)
    
    # Decode the token
    decoded_data = decode_token(token, SECRET)
    
    # Assertions
    assert decoded_data is not None  # 1
    for key, value in token_data.items():
        assert decoded_data[key] == value  # 2

def test_decode_token_invalid_signature():
    """
    Test decoding a token with an invalid signature.

    Assertions:
    1. Ensure that an InvalidJWTToken exception is raised when the secret is wrong.
    """
    token_data = {"user_id": 123}
    token = create_token(token_data, SECRET, expiration_minutes=5)
    
    # Try decoding with the wrong secret
    with pytest.raises(InvalidJWTToken, match="Invalid token received"):
        decode_token(token, "wrongsecret")  # 1

def test_decode_token_expired():
    """
    Test decoding an expired JWT token.

    Assertions:
    1. Ensure that an InvalidJWTToken exception is raised for an expired token.
    """
    token_data = {"user_id": 123}
    token = create_token(token_data, SECRET, expiration_minutes=-1)  # Expired token
    
    # Try decoding the expired token
    with pytest.raises(InvalidJWTToken, match="Invalid token received"):
        decode_token(token, SECRET)  # 1
