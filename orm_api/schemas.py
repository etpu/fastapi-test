from pydantic import BaseModel, Field

from . import config


class User(BaseModel):
    extension: str = Field(..., max_length=20)
    name: str = Field(None, max_length=50)
    group_id: str = Field(None, max_length=20)
    title: str = Field(None, max_length=50)

    class Config:
        orm_mode = True


class Group(BaseModel):
    group_id: str = Field(None, max_length=2, regex=config.REGEX_INT)
    title: str = Field(None, max_length=50, regex=config.REGEX_TITLE)

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    name: str = Field(None, max_length=50, regex=config.REGEX_NAME)
    group_id: str = Field(None, max_length=2, regex=config.REGEX_INT)


class GroupIn(BaseModel):
    title: str = Field(..., max_length=50, regex=config.REGEX_TITLE)
