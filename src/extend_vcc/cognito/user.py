from dataclasses import dataclass
from typing import Any, Dict

from .srp import SRPAuthentication


@dataclass
class UserSRPAuth:
    """User SRP authentication request parameters"""

    auth_flow: str = "USER_SRP_AUTH"
    client_id: str = None
    auth_parameters: Dict[str, str] = None
    client_metadata: Dict = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AuthFlow": self.auth_flow,
            "ClientId": self.client_id,
            "AuthParameters": self.auth_parameters,
            "ClientMetadata": self.client_metadata or {},
        }


@dataclass
class UserSRPResponse:
    """Response from user SRP authentication"""

    challenge_name: str
    challenge_parameters: Dict[str, str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSRPResponse":
        return cls(
            challenge_name=data["ChallengeName"],
            challenge_parameters=data["ChallengeParameters"],
        )


@dataclass
class UserPasswordVerifier:
    """User password verifier request parameters"""

    challenge_name: str = "PASSWORD_VERIFIER"
    client_id: str = None
    challenge_responses: Dict[str, str] = None
    client_metadata: Dict = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ChallengeName": self.challenge_name,
            "ClientId": self.client_id,
            "ChallengeResponses": self.challenge_responses,
            "ClientMetadata": self.client_metadata or {},
        }


@dataclass
class UserPasswordVerifierResponse:
    """Response from user password verification"""

    challenge_name: str
    challenge_parameters: Dict[str, Any]
    session: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPasswordVerifierResponse":
        return cls(
            challenge_name=data["ChallengeName"],
            challenge_parameters=data["ChallengeParameters"],
            session=data["Session"],
        )


async def user_srp_auth(csrp: SRPAuthentication, client_id: str) -> UserSRPResponse:
    """
    Perform user SRP authentication

    Args:
        csrp: SRP authentication instance
        client_id: Cognito client ID

    Returns:
        UserSRPResponse object
    """
    auth = UserSRPAuth(client_id=client_id, auth_parameters=csrp.get_auth_params())

    return auth.to_dict()


async def user_password_verifier(
    csrp: SRPAuthentication, challenge_parameters: Dict[str, str], client_id: str
) -> UserPasswordVerifierResponse:
    """
    Perform user password verification

    Args:
        csrp: SRP authentication instance
        challenge_parameters: Challenge parameters from previous response
        client_id: Cognito client ID

    Returns:
        UserPasswordVerifierResponse object
    """
    challenge_responses = csrp.password_verifier_challenge(challenge_parameters)

    verifier = UserPasswordVerifier(
        client_id=client_id, challenge_responses=challenge_responses
    )

    return verifier.to_dict()
