from __future__ import annotations

import datetime
import uuid
from typing import (
    Annotated,
    Any,
    List,
    Literal,
    NotRequired,
    Optional,
    TypeAlias,
    TypedDict,
)

from pydantic import BaseModel, Field, Json

AuthFactorType: TypeAlias = Literal["totp", "webauthn", "phone"]

AuthFactorStatus: TypeAlias = Literal["unverified", "verified"]

AuthAalLevel: TypeAlias = Literal["aal1", "aal2", "aal3"]

AuthCodeChallengeMethod: TypeAlias = Literal["s256", "plain"]

AuthOneTimeTokenType: TypeAlias = Literal[
    "confirmation_token",
    "reauthentication_token",
    "recovery_token",
    "email_change_token_new",
    "email_change_token_current",
    "phone_change_token",
]

AuthOauthRegistrationType: TypeAlias = Literal["dynamic", "manual"]

AuthOauthAuthorizationStatus: TypeAlias = Literal[
    "pending", "approved", "denied", "expired"
]

AuthOauthResponseType: TypeAlias = Literal["code"]

AuthOauthClientType: TypeAlias = Literal["public", "confidential"]

StorageBuckettype: TypeAlias = Literal["STANDARD", "ANALYTICS", "VECTOR"]

RealtimeEqualityOp: TypeAlias = Literal["eq", "neq", "lt", "lte", "gt", "gte", "in"]

RealtimeAction: TypeAlias = Literal["INSERT", "UPDATE", "DELETE", "TRUNCATE", "ERROR"]


class PublicInstruments(BaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name")


class PublicInstrumentsInsert(TypedDict):
    id: NotRequired[Annotated[int, Field(alias="id")]]
    name: Annotated[str, Field(alias="name")]


class PublicInstrumentsUpdate(TypedDict):
    id: NotRequired[Annotated[int, Field(alias="id")]]
    name: NotRequired[Annotated[str, Field(alias="name")]]


class PublicUserProfiles(BaseModel):
    avatar: str = Field(alias="avatar")
    id: uuid.UUID = Field(alias="id")


class PublicUserProfilesInsert(TypedDict):
    avatar: Annotated[str, Field(alias="avatar")]
    id: Annotated[uuid.UUID, Field(alias="id")]


class PublicUserProfilesUpdate(TypedDict):
    avatar: NotRequired[Annotated[str, Field(alias="avatar")]]
    id: NotRequired[Annotated[uuid.UUID, Field(alias="id")]]
