# models.py
import pydantic
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from .timestamps import TimeStamps
from .uuid import UUID


# Real actual user model
class User(UUID, TimeStamps):
    name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=128)

    class Meta:
        table = "users"  # safer than "user"


# learning model
class UserDB(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100)


# learning model
class UserPydantic(pydantic.BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserPydanticInFakeDB(UserPydantic):
    hashed_password: str
