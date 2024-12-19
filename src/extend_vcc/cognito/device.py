from dataclasses import dataclass
from typing import Any, Dict

from .srp import SRPAuthentication


@dataclass
class DeviceSRPAuth:
    """Device SRP authentication request parameters"""

    challenge_name: str = "DEVICE_SRP_AUTH"
    client_id: str = None
    challenge_responses: Dict[str, str] = None
    session: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ChallengeName": self.challenge_name,
            "ClientId": self.client_id,
            "ChallengeResponses": self.challenge_responses,
            "Session": self.session,
        }


@dataclass
class DeviceSRPResponse:
    """Response from device SRP authentication"""

    challenge_name: str
    challenge_parameters: Dict[str, str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceSRPResponse":
        return cls(
            challenge_name=data["ChallengeName"],
            challenge_parameters=data["ChallengeParameters"],
        )


@dataclass
class DevicePasswordVerifier:
    """Device password verifier request parameters"""

    challenge_name: str = "DEVICE_PASSWORD_VERIFIER"
    client_id: str = None
    challenge_responses: Dict[str, str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ChallengeName": self.challenge_name,
            "ClientId": self.client_id,
            "ChallengeResponses": self.challenge_responses,
        }


@dataclass
class InitialAuthenticationResult:
    """Initial authentication result containing tokens"""

    access_token: str
    refresh_token: str
    expires_in: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InitialAuthenticationResult":
        return cls(
            access_token=data["AccessToken"],
            refresh_token=data["RefreshToken"],
            expires_in=data["ExpiresIn"],
        )


@dataclass
class DevicePasswordVerifierResponse:
    """Response from device password verification"""

    authentication_result: InitialAuthenticationResult
    challenge_parameters: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DevicePasswordVerifierResponse":
        return cls(
            authentication_result=InitialAuthenticationResult.from_dict(
                data["AuthenticationResult"]
            ),
            challenge_parameters=data["ChallengeParameters"],
        )


async def device_srp_auth(
    csrp: SRPAuthentication, session: str, client_id: str
) -> DeviceSRPResponse:
    """
    Perform device SRP authentication

    Args:
        csrp: SRP authentication instance
        session: Session token from previous challenge
        client_id: Cognito client ID

    Returns:
        DeviceSRPResponse object
    """
    auth_params = DeviceSRPAuth(
        client_id=client_id,
        challenge_responses=csrp.get_device_auth_params(),
        session=session,
    )

    return auth_params.to_dict()


async def device_password_verifier(
    csrp: SRPAuthentication,
    user_id: str,
    challenge_parameters: Dict[str, str],
    client_id: str,
) -> DevicePasswordVerifierResponse:
    """
    Perform device password verification

    Args:
        csrp: SRP authentication instance
        user_id: User ID from previous challenge
        challenge_parameters: Challenge parameters from previous response
        client_id: Cognito client ID

    Returns:
        DevicePasswordVerifierResponse object
    """
    challenge_responses = csrp.device_password_verifier_challenge(
        user_id, challenge_parameters
    )

    verifier = DevicePasswordVerifier(
        client_id=client_id, challenge_responses=challenge_responses
    )

    return verifier.to_dict()
