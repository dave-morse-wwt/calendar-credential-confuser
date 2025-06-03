import datetime
import secrets
from typing import Optional, Self
from uuid import uuid4

from ccc_logger import logger
from models.timestamps import TimeStamps
from models.user import User
from models.uuid import UUID
from tortoise import fields
from tortoise.models import Model


class RefreshToken(UUID, TimeStamps):
    user = fields.ForeignKeyField(
        "models.User", related_name="refresh_tokens", on_delete=fields.CASCADE
    )
    token = fields.CharField(
        max_length=255, unique=True
    )  # Use a securely generated random string
    ip_address = fields.CharField(max_length=45, null=True)  # IPv6 support
    user_agent = fields.TextField(null=True)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "refresh_tokens"
        ordering = ["-created_at"]

    def is_expired(self) -> bool:
        return self.expires_at < datetime.datetime.now(datetime.timezone.utc)

    @classmethod
    async def mint(
        cls,
        user: User,
        *,
        ttl_seconds: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "User":
        """
        Mint a new refresh token for the given user.

        Args:
            user (User): The user this token is associated with.
            ttl_seconds (int): Seconds until expiration.
            ip_address (str, optional): IP address of the request (for auditing).
            user_agent (str, optional): User agent string (for tracking device/browser).

        Returns:
            RefreshToken: The newly created refresh token object.
        """
        assert user
        logger.warning(f"{user=} {type(user)=}")
        token_value = secrets.token_urlsafe(64)
        expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=ttl_seconds
        )

        return await cls.create(
            user=user,
            token=token_value,
            expires_at=expires,
            ip_address=ip_address,
            user_agent=user_agent,
        )
