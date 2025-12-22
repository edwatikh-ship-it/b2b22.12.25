from pydantic import BaseModel, Field


class AddUserBlacklistInnRequestDTO(BaseModel):
    inn: str = Field(min_length=10, max_length=12)
    reason: str | None = None


class UserBlacklistInnItemDTO(BaseModel):
    id: int
    inn: str
    supplierid: int | None = None
    suppliername: str | None = None
    checkodata: dict | None = None
    reason: str | None = None
    createdat: str


class UserBlacklistInnListResponseDTO(BaseModel):
    items: list[UserBlacklistInnItemDTO]
    limit: int
    offset: int
    total: int


class AddBlacklistDomainRequestDTO(BaseModel):
    domain: str = Field(min_length=1)


class BlacklistDomainsListResponseDTO(BaseModel):
    items: list[str]
    limit: int
    total: int
