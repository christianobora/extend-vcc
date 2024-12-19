from datetime import datetime, timedelta
from threading import Lock
from typing import Dict

import requests

from extend_vcc import Authenticator

from .auth import AuthParams
from .srp import SRPAuthentication

CLIENT_ID = "79k2g0t0ujq2tfchb23d5j6htk"
USER_POOL_NAME = "pN4CuZHEc"


class Cognito(Authenticator):
    """
    AWS Cognito authenticator using SRP authentication flow
    """

    def __init__(self, auth: AuthParams):
        self.csrp = SRPAuthentication(auth)
        self._access_token = ""
        self._refresh_token = ""
        self._expiry = datetime.now()
        self.http = requests.Session()
        self._lock = Lock()

        # Set default headers
        self.http.headers.update(
            {
                "accept-language": "en-US,en;q=0.7",
                "cache-control": "no-cache",
                "dnt": "1",
                "origin": "https://app.paywithextend.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://app.paywithextend.com/",
                "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "X-Amz-User-Agent": "aws-amplify/5.0.4 auth framework/1",
                "Content-Type": "application/x-amz-json-1.1",
            }
        )

    def expiry(self) -> datetime:
        return self._expiry

    def _request(self, target: str, body: Dict) -> Dict:
        """Make a request to Cognito service"""
        headers = {"X-Amz-Target": target}

        response = self.http.post(
            "https://cognito-idp.us-east-1.amazonaws.com/", headers=headers, json=body
        )

        if response.status_code != 200:
            raise Exception(f"Cognito error: {response.text}")

        return response.json()

    def login(self) -> str:
        """Perform initial login flow"""
        # Step 1: User SRP Auth
        user_challenge = self._user_srp_auth()
        if user_challenge["ChallengeName"] != "PASSWORD_VERIFIER":
            raise Exception(
                f"Unexpected user challenge: {user_challenge['ChallengeName']}"
            )

        # Step 2: Password Verifier
        device_auth = self._user_password_verifier(
            user_challenge["ChallengeParameters"]
        )
        if device_auth["ChallengeName"] != "DEVICE_SRP_AUTH":
            raise Exception(
                f"Unexpected device challenge: {device_auth['ChallengeName']}"
            )

        # Step 3: Device SRP Auth
        device_challenge = self._device_srp_auth(device_auth["Session"])

        # Step 4: Device Password Verifier
        tokens = self._device_password_verifier(
            user_challenge["ChallengeParameters"]["USER_ID_FOR_SRP"],
            device_challenge["ChallengeParameters"],
        )

        # Store tokens
        self._access_token = tokens["AuthenticationResult"]["AccessToken"]
        self._refresh_token = tokens["AuthenticationResult"]["RefreshToken"]
        self._expiry = datetime.now() + timedelta(
            seconds=tokens["AuthenticationResult"]["ExpiresIn"]
        )

        return self._access_token

    def refresh(self) -> str:
        """Refresh the access token"""
        response = self._request(
            "AWSCognitoIdentityProviderService.InitiateAuth",
            {
                "ClientId": CLIENT_ID,
                "AuthFlow": "REFRESH_TOKEN_AUTH",
                "AuthParameters": {
                    "REFRESH_TOKEN": self._refresh_token,
                    "DEVICE_KEY": self.csrp.auth.device_key,
                },
                "ClientMetadata": {},
            },
        )

        self._access_token = response["AuthenticationResult"]["AccessToken"]
        self._expiry = datetime.now() + timedelta(
            seconds=response["AuthenticationResult"]["ExpiresIn"]
        )

        return self._access_token

    def get_access_token(self) -> str:
        """Get current access token or obtain a new one"""
        with self._lock:
            if not self._refresh_token:
                return self.login()

            if self._expires_soon():
                return self.refresh()

            return self._access_token

    def _expires_soon(self) -> bool:
        """Check if token expires within 5 minutes"""
        return datetime.now() + timedelta(minutes=5) > self._expiry

    def _user_srp_auth(self) -> Dict:
        """Initiate user SRP authentication"""
        return self._request(
            "AWSCognitoIdentityProviderService.InitiateAuth",
            {
                "AuthFlow": "USER_SRP_AUTH",
                "ClientId": CLIENT_ID,
                "AuthParameters": self.csrp.get_auth_params(),
                "ClientMetadata": {},
            },
        )

    def _user_password_verifier(self, challenge_parameters: Dict) -> Dict:
        """Complete user password verification"""
        challenge_responses = self.csrp.password_verifier_challenge(
            challenge_parameters
        )

        return self._request(
            "AWSCognitoIdentityProviderService.RespondToAuthChallenge",
            {
                "ChallengeName": "PASSWORD_VERIFIER",
                "ClientId": CLIENT_ID,
                "ChallengeResponses": challenge_responses,
                "ClientMetadata": {},
            },
        )

    def _device_srp_auth(self, session: str) -> Dict:
        """Initiate device SRP authentication"""
        return self._request(
            "AWSCognitoIdentityProviderService.RespondToAuthChallenge",
            {
                "ChallengeName": "DEVICE_SRP_AUTH",
                "ClientId": CLIENT_ID,
                "ChallengeResponses": self.csrp.get_device_auth_params(),
                "Session": session,
            },
        )

    def _device_password_verifier(
        self, user_id: str, challenge_parameters: Dict
    ) -> Dict:
        """Complete device password verification"""
        challenge_responses = self.csrp.device_password_verifier_challenge(
            user_id, challenge_parameters
        )

        return self._request(
            "AWSCognitoIdentityProviderService.RespondToAuthChallenge",
            {
                "ChallengeName": "DEVICE_PASSWORD_VERIFIER",
                "ClientId": CLIENT_ID,
                "ChallengeResponses": challenge_responses,
            },
        )
