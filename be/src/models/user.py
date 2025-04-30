# models.py
import pydantic
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class UserDB(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100)


# Pardon the "User" name collision chaos - working through an example.
class UserPydantic(pydantic.BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
