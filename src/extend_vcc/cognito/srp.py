import base64
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Dict

from .auth import AuthParams

N_HEX = """FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1
29024E088A67CC74020BBEA63B139B22514A08798E3404DD
EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245
E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED
EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D
C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F
83655D23DCA3AD961C62F356208552BB9ED529077096966D
670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B
E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9
DE2BCBF6955817183995497CEA956AE515D2261898FA0510
15728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64
ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7
ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6B
F12FFA06D98A0864D87602733EC86A64521F2B18177B200C
BBE117577A615D6C770988C0BAD946E208E24FA074E5AB31
43DB5BFCE0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF""".replace(
    "\n", ""
)

G_HEX = "2"
INFO_BITS = "Caldera Derived Key"


def hex_to_long(hex_string: str) -> int:
    return int(hex_string, 16)


def long_to_hex(n: int) -> str:
    return hex(n)[2:]


def hex_hash(hex_str: str) -> str:
    return hashlib.sha256(bytes.fromhex(hex_str)).hexdigest()


def pad_hex(hex_str: str) -> str:
    """Pad hex string to ensure proper format"""
    if len(hex_str) % 2 == 1:
        hex_str = f"0{hex_str}"
    elif any(c in "89ABCDEFabcdef" for c in hex_str[0]):
        hex_str = f"00{hex_str}"
    return hex_str


def get_random(nbytes: int) -> int:
    """Generate random number with given number of bytes"""
    return int.from_bytes(secrets.token_bytes(nbytes), "big")


class SRPAuthentication:
    def __init__(self, auth: AuthParams):
        self.auth = auth

        # Initialize values
        self.N = hex_to_long(N_HEX)
        self.g = hex_to_long(G_HEX)
        self.k = hex_to_long(hex_hash("00" + N_HEX + "0" + G_HEX))

        # Generate a random value
        self.a = self._generate_random_small_a()
        self.A = self._calculate_a()

    def _generate_random_small_a(self) -> int:
        """Generate random small 'a' value"""
        random_long = get_random(128)
        return random_long % self.N

    def _calculate_a(self) -> int:
        """Calculate 'A' value"""
        A = pow(self.g, self.a, self.N)
        if A % self.N == 0:
            raise ValueError("Safety check for A failed. A must not be divisible by N")
        return A

    def get_auth_params(self) -> Dict[str, str]:
        """Get authentication parameters for initial request"""
        return {"USERNAME": self.auth.username, "SRP_A": long_to_hex(self.A)}

    def get_device_auth_params(self) -> Dict[str, str]:
        """Get device authentication parameters"""
        return {
            "USERNAME": self.auth.username,
            "SRP_A": long_to_hex(self.A),
            "DEVICE_KEY": self.auth.device_key,
        }

    def password_verifier_challenge(
        self, challenge_params: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate password verifier challenge response"""
        username = challenge_params["USERNAME"]
        user_id = challenge_params["USER_ID_FOR_SRP"]
        salt_hex = challenge_params["SALT"]
        srp_b_hex = challenge_params["SRP_B"]
        secret_block_b64 = challenge_params["SECRET_BLOCK"]

        # Calculate HKDF
        hkdf = self._get_password_authentication_key(
            "pN4CuZHEc",
            user_id,
            self.auth.password,
            hex_to_long(srp_b_hex),
            hex_to_long(salt_hex),
        )

        # Generate timestamp
        timestamp = datetime.now().strftime("%a %b %d %H:%M:%S UTC %Y")

        # Get secret block as bytes - no decoding needed
        secret_block = base64.b64decode(secret_block_b64)

        # Create message using bytes concatenation
        msg = (
            f"pN4CuZHEc{user_id}".encode("utf-8")
            + secret_block
            + timestamp.encode("utf-8")
        )

        # Calculate signature
        hmac_obj = hmac.new(hkdf, msg, hashlib.sha256)
        signature = base64.b64encode(hmac_obj.digest()).decode("utf-8")

        return {
            "TIMESTAMP": timestamp,
            "USERNAME": username,
            "PASSWORD_CLAIM_SECRET_BLOCK": secret_block_b64,
            "PASSWORD_CLAIM_SIGNATURE": signature,
            "DEVICE_KEY": self.auth.device_key,
        }

    def device_password_verifier_challenge(
        self, user_id: str, challenge_params: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate device password verifier challenge response"""
        salt_hex = challenge_params["SALT"]
        srp_b_hex = challenge_params["SRP_B"]
        secret_block_b64 = challenge_params["SECRET_BLOCK"]

        # Calculate HKDF
        hkdf = self._get_password_authentication_key(
            self.auth.device_group_key,
            self.auth.device_key,
            self.auth.device_password,
            hex_to_long(srp_b_hex),
            hex_to_long(salt_hex),
        )

        # Generate timestamp
        timestamp = datetime.now().strftime("%a %b %d %H:%M:%S UTC %Y")

        # Get secret block as bytes - no decoding needed
        secret_block = base64.b64decode(secret_block_b64)

        # Create message using bytes concatenation
        msg = (
            f"{self.auth.device_group_key}{self.auth.device_key}".encode("utf-8")
            + secret_block
            + timestamp.encode("utf-8")
        )

        # Calculate signature
        hmac_obj = hmac.new(hkdf, msg, hashlib.sha256)
        signature = base64.b64encode(hmac_obj.digest()).decode("utf-8")

        return {
            "TIMESTAMP": timestamp,
            "USERNAME": user_id,
            "PASSWORD_CLAIM_SECRET_BLOCK": secret_block_b64,
            "PASSWORD_CLAIM_SIGNATURE": signature,
            "DEVICE_KEY": self.auth.device_key,
        }

    def _get_password_authentication_key(
        self, pool_name: str, username: str, password: str, big_b: int, salt: int
    ) -> bytes:
        """
        Calculate the password authentication key
        """
        # Calculate U value
        u = self._calculate_u(self.A, big_b)

        # Calculate x value
        user_pass = f"{pool_name}{username}:{password}"
        user_pass_hash = hashlib.sha256(user_pass.encode()).hexdigest()
        x = hex_to_long(hex_hash(pad_hex(long_to_hex(salt)) + user_pass_hash))

        # Calculate S value
        g_mod_pow_xn = pow(self.g, x, self.N)
        int_val1 = (big_b - (self.k * g_mod_pow_xn)) % self.N
        int_val2 = (self.a + (u * x)) % (self.N - 1)
        s = pow(int_val1, int_val2, self.N)

        # Compute HKDF
        return self._compute_hkdf(pad_hex(long_to_hex(s)), pad_hex(long_to_hex(u)))

    def _calculate_u(self, big_a: int, big_b: int) -> int:
        """Calculate the U value for SRP"""
        return hex_to_long(
            hex_hash(pad_hex(long_to_hex(big_a)) + pad_hex(long_to_hex(big_b)))
        )

    def _compute_hkdf(self, ikm_hex: str, salt_hex: str) -> bytes:
        """Compute the HKDF value"""
        ikm = bytes.fromhex(ikm_hex)
        salt = bytes.fromhex(salt_hex)

        # Extract
        extractor = hmac.new(salt, ikm, hashlib.sha256)
        prk = extractor.digest()

        # Expand
        info_bits_update = INFO_BITS.encode() + b"\x01"
        extractor = hmac.new(prk, info_bits_update, hashlib.sha256)
        hmac_hash = extractor.digest()

        return hmac_hash[:16]
