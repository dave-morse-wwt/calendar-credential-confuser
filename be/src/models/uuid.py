import uuid

from tortoise import fields
from tortoise.models import Model


class UUID(Model):
    """Abstract model to add UUID primary key."""

    id = fields.UUIDField(pk=True, default=uuid.uuid4)

    class Meta:
        abstract = True
