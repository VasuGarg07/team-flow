from datetime import timedelta

import pytest

from app.security import create_access_token, create_refresh_token, create_token, decode_access_token, hash_password, verify_password
from app.errors import UnauthorizedError


def test_right_password() -> None:
    hashed = hash_password("right_password")
    result = verify_password("right_password", hashed)
    assert result is True

def test_wrong_password() -> None:
    hashed = hash_password("right_password")
    result = verify_password("wrong_password", hashed)
    assert result is False

def test_hash_password_twice() -> None:
    hashed_1 = hash_password("right_password")
    hashed_2 = hash_password("right_password")
    result_1 = verify_password("right_password", hashed_1)
    result_2 = verify_password("right_password", hashed_2)
    assert hashed_1 != hashed_2 and (result_1 and result_2) is True

def test_check_hashed_password_value_and_format() -> None:
    hashed = hash_password("right_password")
    assert hashed != "right_password" and hashed.startswith("$argon2")

def test_access_token_round_trip() -> None:
    assert decode_access_token(create_access_token(7)) == 7

def test_refresh_token_is_rejected_as_access_token() -> None:
    refresh_token = create_refresh_token(1)

    with pytest.raises(UnauthorizedError):
        decode_access_token(refresh_token)

def test_expired_token_is_rejected() -> None:
    expired_token = create_token(1, "access", timedelta(seconds=-1))
    with pytest.raises(UnauthorizedError):
        decode_access_token(expired_token)

def test_tampered_token_is_rejected() -> None:
    access_token = create_access_token(1)
    tampered_token = access_token + "test"
    with pytest.raises(UnauthorizedError):
        decode_access_token(tampered_token)

def test_garbage_token_is_rejected() -> None:
    with pytest.raises(UnauthorizedError):
        decode_access_token("not-a-token")