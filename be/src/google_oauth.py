import logging
import os
from typing import Annotated

from pydantic import BaseModel, HttpUrl, StringConstraints, constr

logger = logging.getLogger("uvicorn")  # uvicorn logger is colorful


class GoogleOAuthConfig(BaseModel):
    class Web(BaseModel):
        client_id: Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                to_lower=True,
                pattern=r"^[\w-]+\.apps\.googleusercontent\.com$",
            ),
        ]
        project_id: str
        auth_uri: HttpUrl
        token_uri: HttpUrl
        auth_provider_x509_cert_url: HttpUrl
        client_secret: str

    web: Web


def load_google_oauth_config() -> GoogleOAuthConfig:
    logger.info("Attempting decoding of $GOOGLE_OAUTH_JSON")
    return GoogleOAuthConfig.model_validate_json(os.environ["GOOGLE_OAUTH_JSON"])
