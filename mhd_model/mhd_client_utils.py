import datetime
import hashlib
import logging
import uuid
from pathlib import Path

import jwt
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def create_rs256_token(
    private_pem: bytes, public_pem: bytes, payload_data: dict, delta: relativedelta
):
    """Creates a JWT signed with RS256 using the provided private PEM."""
    # Define standard payload with expiration and security claims
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "iss": payload_data.get("sub"),
        "exp": now + delta,
        "nbf": now,
        "iat": now,
        "jti": str(uuid.uuid4()),
        **payload_data,
    }

    # Generate a Key ID (kid) from the public key hash
    kid = hashlib.sha256(public_pem).hexdigest()[:16]

    # Sign the payload using the private key, specifying explicit headers
    token = jwt.encode(
        payload,
        private_pem,
        algorithm="RS256",
        headers={"typ": "JWT", "alg": "RS256", "kid": kid},
    )
    return token


def validate_repository_signed_jwt_token(
    signed_jwt_token: str,
    audience: None | str = None,
    public_key: None | str = None,
) -> None | tuple[dict, str]:
    token = signed_jwt_token
    options = {"require": ["exp", "sub", "iat", "sub"]}
    public_key = public_key or ""
    message = None
    decoded = None
    try:
        decoded: dict[str, str] = jwt.decode(
            jwt=token, key="", options={"verify_signature": False}
        )
        if public_key:
            decoded = jwt.decode(
                jwt=token,
                key=public_key,
                options=options,
                audience=audience,
                algorithms=["RS256"],
            )
            message = "Validation of the signed JWT token is skipped."
            logger.info("Signed JWT token is validated.")
        else:
            message = "Validation of the signed JWT token is skipped."
            logger.info(message)
    except Exception as ex:
        message = f"Validation of the signed JWT token failed: {ex}"
    return decoded, message


def create_signed_jwt(
    repository_name: str,
    private_key_path: Path,
    public_key_path: Path,
    validity_period_in_days: int,
    signed_jwt_token_path: None | Path = None,
    audience: str = "https://www.metabolomicshub.org",
):
    delta = relativedelta(days=validity_period_in_days)
    logger.info("Loading RS256 key pair...")
    # Security check: verify private key permissions are restrictive (0o600)
    if (private_key_path.stat().st_mode & 0o777) != 0o600:
        logger.warning(
            "Security vulnerability: private_key.pem has insecure permissions! "
            "Please update its permission. e.g. run 'chmod 600 %s'",
            private_key_path,
        )

    private_pem = private_key_path.read_bytes()
    public_pem = public_key_path.read_bytes()
    logger.info("Keys are loaded")

    # Define your JWT payload
    payload_data = {"sub": repository_name, "aud": audience}

    logger.info("Creating Signed Token...")
    token = create_rs256_token(private_pem, public_pem, payload_data, delta)

    if signed_jwt_token_path:
        signed_jwt_token_path.parent.mkdir(exist_ok=True, parents=True)
        signed_jwt_token_path.write_text(token)
        logger.info("JWT token is saved as %s", signed_jwt_token_path)
    return token
