from dataclasses import dataclass


@dataclass
class AuthParams:
    """Authentication parameters for Cognito"""

    username: str
    password: str
    device_key: str
    device_password: str
    device_group_key: str
