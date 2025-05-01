from tortoise import fields
from tortoise.models import Model


class TimeStamps(Model):
    """Abstract model to add created_at and updated_at timestamps."""

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
