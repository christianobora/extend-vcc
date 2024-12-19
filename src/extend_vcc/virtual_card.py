from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from .types import (
    Address,
    Asset,
    Currency,
    PaginatedResponse,
    PaginationOptions,
    Time,
    User,
)


class VirtualCardType(str, Enum):
    STANDARD = "STANDARD"


class VirtualCardStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"


@dataclass
class VirtualCardImage:
    id: str
    content_type: str
    urls: Asset
    text_color_rgba: str
    has_text_shadow: bool
    shadow_text_color_rgba: str

    @classmethod
    def from_dict(cls, data: dict) -> "VirtualCardImage":
        return cls(
            id=data["id"],
            content_type=data["contentType"],
            urls=Asset(**data["urls"]),
            text_color_rgba=data["textColorRGBA"],
            has_text_shadow=data["hasTextShadow"],
            shadow_text_color_rgba=data["shadowTextColorRGBA"],
        )


@dataclass
class VirtualCardFeatures:
    recurrence: bool
    mcc_control: bool
    qbo_report_enabled: bool

    @classmethod
    def from_dict(cls, data: dict) -> "VirtualCardFeatures":
        return cls(
            recurrence=data["recurrence"],
            mcc_control=data["mccControl"],
            qbo_report_enabled=data["qboReportEnabled"],
        )


@dataclass
class VirtualCardIssuer:
    id: str
    name: str
    code: str

    @classmethod
    def from_dict(cls, data: dict) -> "VirtualCardIssuer":
        return cls(id=data["id"], name=data["name"], code=data["code"])


@dataclass
class CreateVirtualCardOptions:
    credit_card_id: str
    display_name: str
    balance_cents: int
    currency: Currency
    notes: str
    valid_to: datetime
    recipient: str


@dataclass
class UpdateVirtualCardOptions:
    credit_card_id: str
    display_name: str
    balance_cents: int
    recurs: bool
    valid_to: datetime
    currency: Currency
    receipt_rules_exempt: bool


@dataclass
class VirtualCard:
    id: str
    status: VirtualCardStatus
    recipient_id: str
    recipient: User
    cardholder_id: str
    cardholder: User
    vcn: Optional[str]
    security_code: Optional[str]
    last_updated_by: Optional[User]
    card_image: VirtualCardImage
    card_type: str
    display_name: str
    expires: Time
    currency: str
    limit_cents: int
    balance_cents: int
    spent_cents: int
    lifetime_spent_cents: int
    last4: str
    number_format: str
    valid_from: str
    valid_to: str
    timezone: str
    credit_card_id: str
    recurs: bool
    created_at: str
    updated_at: str
    address: Address
    features: VirtualCardFeatures
    has_plastic_card: bool
    active_until: str
    network: str
    company_name: str
    credit_card_display_name: VirtualCardIssuer
    receipt_rules_exempt: bool
    is_bill_pay: bool

    @classmethod
    def from_dict(cls, data: dict) -> "VirtualCard":
        return cls(
            id=data["id"],
            status=VirtualCardStatus(data["status"]),
            recipient_id=data["recipientId"],
            recipient=User.from_dict(data["recipient"]),
            cardholder_id=data["cardholderId"],
            cardholder=User.from_dict(data["cardholder"]),
            vcn=data.get("vcn"),
            security_code=data.get("securityCode"),
            last_updated_by=(
                User.from_dict(data["lastUpdatedBy"])
                if "lastUpdatedBy" in data
                else None
            ),
            card_image=VirtualCardImage.from_dict(data["cardImage"]),
            card_type=data["cardType"],
            display_name=data["displayName"],
            expires=Time.from_string(data["expires"]),
            currency=data["currency"],
            limit_cents=data["limitCents"],
            balance_cents=data["balanceCents"],
            spent_cents=data["spentCents"],
            lifetime_spent_cents=data["lifetimeSpentCents"],
            last4=data["last4"],
            number_format=data["numberFormat"],
            valid_from=data["validFrom"],
            valid_to=data["validTo"],
            timezone=data["timezone"],
            credit_card_id=data["creditCardId"],
            recurs=data["recurs"],
            created_at=data["createdAt"],
            updated_at=data["updatedAt"],
            address=Address.from_dict(data["address"]),
            features=VirtualCardFeatures.from_dict(data["features"]),
            has_plastic_card=data["hasPlasticCard"],
            active_until=data["activeUntil"],
            network=data["network"],
            company_name=data["companyName"],
            credit_card_display_name=VirtualCardIssuer.from_dict(data["issuer"]),
            receipt_rules_exempt=data["receiptRulesExempt"],
            is_bill_pay=data["isBillPay"],
        )


@dataclass
class VirtualCardResponse:
    virtual_card: VirtualCard

    @classmethod
    def from_dict(cls, data: dict) -> "VirtualCardResponse":
        return cls(virtual_card=VirtualCard.from_dict(data["virtualCard"]))


@dataclass
class ListVirtualCardsOptions:
    pagination_options: PaginationOptions
    cardholder_or_viewer: str
    issued: bool
    statuses: List[VirtualCardStatus]


@dataclass
class ListVirtualCardsResponse(PaginatedResponse):
    virtual_cards: List[VirtualCard]

    def items(self) -> List[VirtualCard]:
        return self.virtual_cards

    @classmethod
    def from_dict(cls, data: dict) -> "ListVirtualCardsResponse":
        return cls(
            virtual_cards=[
                VirtualCard.from_dict(card) for card in data["virtualCards"]
            ],
            pagination=data["pagination"],
        )


@dataclass
class BulkCreateVirtualCard:
    card_type: VirtualCardType
    recipient: str
    display_name: str
    balance_cents: int
    valid_to: datetime
    notes: str = ""


@dataclass
class BulkVirtualCardRecord:
    credit_card_id: str
    recipient: str
    cardholder: str
    display_name: str
    direct: bool
    balance_cents: int
    currency: str
    valid_to_date: List[int]
    recurs: bool
    has_plastic_card: bool
    single_exact_pay: bool
    is_push: bool
    is_request: bool
    until_date: List[int]

    @classmethod
    def from_dict(cls, data: dict) -> "BulkVirtualCardRecord":
        return cls(
            credit_card_id=data["creditCardId"],
            recipient=data["recipient"],
            cardholder=data["cardholder"],
            display_name=data["displayName"],
            direct=data["direct"],
            balance_cents=data["balanceCents"],
            currency=data["currency"],
            valid_to_date=data["validToDate"],
            recurs=data["recurs"],
            has_plastic_card=data["hasPlasticCard"],
            single_exact_pay=data["singleExactPay"],
            is_push=data["isPush"],
            is_request=data["isRequest"],
            until_date=data["untilDate"],
        )


@dataclass
class BulkVirtualCardUploadTask:
    task_id: str
    status: str
    record: BulkVirtualCardRecord

    @classmethod
    def from_dict(cls, data: dict) -> "BulkVirtualCardUploadTask":
        return cls(
            task_id=data["taskId"],
            status=data["status"],
            record=BulkVirtualCardRecord.from_dict(data["record"]),
        )


@dataclass
class BulkVirtualCardUploadStatus:
    INITIATED = "Initiated"
    COMPLETED = "Completed"


@dataclass
class BulkVirtualCardTask:
    task_id: str
    status: BulkVirtualCardUploadStatus
    virtual_card_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "BulkVirtualCardTask":
        return cls(
            task_id=data["taskId"],
            status=BulkVirtualCardUploadStatus(data["status"]),
            virtual_card_id=data["virtualCardId"],
        )


@dataclass
class BulkVirtualCardUpload:
    id: str
    user_id: str
    credit_card_id: str
    created_at: Time
    updated_at: Time
    tasks: List[BulkVirtualCardTask]

    @classmethod
    def from_dict(cls, data: dict) -> "BulkVirtualCardUpload":
        return cls(
            id=data["id"],
            user_id=data["userId"],
            credit_card_id=data["creditCardId"],
            created_at=Time.from_string(data["createdAt"]),
            updated_at=Time.from_string(data["updatedAt"]),
            tasks=[BulkVirtualCardTask.from_dict(task) for task in data["tasks"]],
        )


@dataclass
class BulkVirtualCardPush:
    bulk_virtual_card_upload_id: str
    tasks: List[BulkVirtualCardUploadTask]

    @classmethod
    def from_dict(cls, data: dict) -> "BulkVirtualCardPush":
        return cls(
            bulk_virtual_card_upload_id=data["bulkVirtualCardUploadId"],
            tasks=[BulkVirtualCardUploadTask.from_dict(task) for task in data["tasks"]],
        )


@dataclass
class BulkVirtualCardPushResponse:
    bulk_virtual_card_push: BulkVirtualCardPush
    invalid_emails: List[str]
    csv_virtual_card_push: BulkVirtualCardPush

    @classmethod
    def from_dict(cls, data: dict) -> "BulkVirtualCardPushResponse":
        return cls(
            bulk_virtual_card_push=BulkVirtualCardPush.from_dict(
                data["bulkVirtualCardPush"]
            ),
            invalid_emails=data["invalidEmails"],
            csv_virtual_card_push=BulkVirtualCardPush.from_dict(
                data["csvVirtualCardPush"]
            ),
        )
