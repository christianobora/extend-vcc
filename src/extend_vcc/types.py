from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar


class Currency(str, Enum):
    USD = "USD"


class Time(datetime):
    """Custom datetime class with specific serialization format"""

    TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    def __str__(self) -> str:
        return self.strftime(self.TIME_FORMAT)[:-3] + "+0000"

    @classmethod
    def from_string(cls, value: str) -> "Time":
        if not value:
            return None
        # Remove timezone for parsing
        value = value[:-5] if value.endswith("+0000") else value
        return cls.strptime(value, cls.TIME_FORMAT)


@dataclass
class Organization:
    id: str
    role: str
    joined_at: str
    explicit: bool

    @classmethod
    def from_dict(cls, data: dict) -> "Organization":
        return cls(
            id=data["id"],
            role=data["role"],
            joined_at=data["joinedAt"],
            explicit=data["explicit"],
        )


@dataclass
class Address:
    address1: str
    city: str
    province: str
    postal: str
    country: str

    @classmethod
    def from_dict(cls, data: dict) -> "Address":
        return cls(
            address1=data["address1"],
            city=data["city"],
            province=data["province"],
            postal=data["postal"],
            country=data["country"],
        )


@dataclass
class Asset:
    large: str
    medium: str
    small: str

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        return cls(large=data["large"], medium=data["medium"], small=data["small"])


@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    email: str
    phone_iso_country: Optional[str]
    avatar_type: str
    created_at: str
    updated_at: str
    currency: str
    locale: str
    timezone: str
    verified: bool
    organization: Organization
    organization_id: str
    organization_role: str

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            first_name=data["firstName"],
            last_name=data["lastName"],
            email=data["email"],
            phone_iso_country=data.get("phoneIsoCountry"),
            avatar_type=data["avatarType"],
            created_at=data["createdAt"],
            updated_at=data["updatedAt"],
            currency=data["currency"],
            locale=data["locale"],
            timezone=data["timezone"],
            verified=data["verified"],
            organization=Organization.from_dict(data["organization"]),
            organization_id=data["organizationId"],
            organization_role=data["organizationRole"],
        )


@dataclass
class Pagination:
    page: int
    page_item_count: int
    total_items: int
    number_of_pages: int

    @classmethod
    def from_dict(cls, data: dict) -> "Pagination":
        return cls(
            page=data["page"],
            page_item_count=data["pageItemCount"],
            total_items=data["totalItems"],
            number_of_pages=data["numberOfPages"],
        )


@dataclass
class PaginationResponse:
    pagination: Pagination

    def get_pagination(self) -> Pagination:
        return self.pagination

    @classmethod
    def from_dict(cls, data: dict) -> "PaginationResponse":
        return cls(pagination=Pagination.from_dict(data["pagination"]))


T = TypeVar("T")


class PaginatedResponse(Generic[T]):
    def __init__(self, items: List[T], pagination: Pagination):
        self.items = items
        self.pagination = pagination

    def get_pagination(self) -> Pagination:
        return self.pagination


class SortDirection(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class PaginationOptions:
    page: int = 0
    count: int = 20
    sort_direction: SortDirection = SortDirection.DESC
    sort_field: str = "createdAt"
