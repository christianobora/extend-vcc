from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from extend_vcc.async_client import AsyncClient
from extend_vcc.types import Currency
from extend_vcc.virtual_card import (
    CreateVirtualCardOptions,
    ListVirtualCardsOptions,
    PaginationOptions,
    VirtualCardStatus,
)


@pytest.mark.asyncio
async def test_create_virtual_card():
    # Mock auth
    auth = MagicMock()
    auth.get_access_token = AsyncMock(return_value="test-token")

    # Mock response
    mock_response = {
        "virtualCard": {
            "id": "vc_dummy_id",
            "status": "ACTIVE",
            "recipientId": "u_dummy_recipient_id",
            "recipient": {
                "id": "u_dummy_recipient_id",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "avatarType": "DEFAULT",
                "createdAt": "2024-12-01T00:00:00.000+0000",
                "updatedAt": "2024-12-01T12:00:00.000+0000",
                "currency": "USD",
                "locale": "en-US",
                "timezone": "America/New_York",
                "verified": True,
                "organization": {
                    "id": "org_dummy_id",
                    "role": "OWNER",
                    "joinedAt": "2024-12-01T00:00:00.000+0000",
                    "explicit": True,
                },
                "organizationId": "org_dummy_id",
                "organizationRole": "OWNER",
            },
            "cardholderId": "u_dummy_cardholder_id",
            "cardholder": {
                "id": "u_dummy_cardholder_id",
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "jane.smith@example.com",
                "avatarType": "DEFAULT",
                "createdAt": "2024-12-01T00:00:00.000+0000",
                "updatedAt": "2024-12-01T12:00:00.000+0000",
                "currency": "USD",
                "locale": "en-US",
                "timezone": "America/New_York",
                "verified": True,
                "organization": {
                    "id": "org_dummy_id",
                    "role": "ADMIN",
                    "joinedAt": "2024-12-01T00:00:00.000+0000",
                    "explicit": True,
                },
                "organizationId": "org_dummy_id",
                "organizationRole": "ADMIN",
            },
            "cardImage": {
                "id": "im_dummy_id",
                "contentType": "image/png",
                "urls": {
                    "large": "https://example.com/large.png",
                    "medium": "https://example.com/medium.png",
                    "small": "https://example.com/small.png",
                },
                "textColorRGBA": "rgba(255,255,255,1)",
                "hasTextShadow": False,
                "shadowTextColorRGBA": "rgba(0,0,0,1)",
            },
            "cardType": "STANDARD",
            "displayName": "Test Card",
            "expires": "2029-12-19T00:00:00.000+0000",
            "currency": "USD",
            "limitCents": 10000,
            "balanceCents": 10000,
            "spentCents": 500,
            "lifetimeSpentCents": 500,
            "last4": "1234",
            "numberFormat": "XXXX-XXXX-XXXX-1234",
            "validFrom": "2024-12-01T00:00:00.000+0000",
            "validTo": "2025-01-01T00:00:00.000+0000",
            "timezone": "America/New_York",
            "creditCardId": "cc_dummy_id",
            "recurs": False,
            "notes": "Test note",
            "createdAt": "2024-12-01T00:00:00.000+0000",
            "updatedAt": "2024-12-01T12:00:00.000+0000",
            "address": {
                "address1": "123 Main St",
                "city": "New York",
                "province": "NY",
                "postal": "10001",
                "country": "US",
            },
            "features": {
                "recurrence": True,
                "mccControl": True,
                "qboReportEnabled": True,
            },
            "hasPlasticCard": False,
            "activeUntil": "2025-01-01T00:00:00.000+0000",
            "network": "VISA",
            "companyName": "Example Corp",
            "creditCardDisplayName": "Example Virtual Card",
            "issuer": {"id": "iss_dummy_id", "name": "Example Bank", "code": "EXB"},
            "receiptRulesExempt": False,
            "isBillPay": False,
            "expenseCategories": [],
            "receiptAttachments": [],
            "referenceFields": [],
            "lastUpdatedBy": {
                "id": "u_dummy_last_updated_id",
                "firstName": "Admin",
                "lastName": "User",
                "email": "admin@example.com",
                "avatarType": "DEFAULT",
                "createdAt": "2024-12-01T00:00:00.000+0000",
                "updatedAt": "2024-12-01T12:00:00.000+0000",
                "currency": "USD",
                "locale": "en-US",
                "timezone": "America/New_York",
                "verified": True,
                "organization": {
                    "id": "org_dummy_id",
                    "role": "OWNER",
                    "joinedAt": "2024-12-01T00:00:00.000+0000",
                    "explicit": True,
                },
                "organizationId": "org_dummy_id",
                "organizationRole": "OWNER",
            },
        }
    }

    # Create client with mocked session
    session = AsyncMock()
    session.request = AsyncMock()
    session.request.return_value.__aenter__.return_value.status = 200
    session.request.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=mock_response
    )

    async with AsyncClient(auth, session=session) as client:
        # Create card options
        options = CreateVirtualCardOptions(
            credit_card_id="cc_dummy_id",
            display_name="Test Card",
            balance_cents=10000,
            currency=Currency.USD,
            valid_to=datetime.now() + timedelta(days=30),
            recipient="recipient@example.com",
            notes="Test note",
        )

        # Test card creation
        card = await client.create_virtual_card(options)

        assert card.id == "vc_dummy_id"
        assert card.display_name == "Test Card"
        assert card.balance_cents == 10000


@pytest.mark.asyncio
async def test_list_virtual_cards():
    # Mock auth
    auth = MagicMock()
    auth.get_access_token = AsyncMock(return_value="test-token")

    # Mock responses for pagination
    mock_responses = [
        {
            "virtualCards": [
                {"id": "card1", "displayName": "Test Card 1"},
                {"id": "card2", "displayName": "Test Card 2"},
            ],
            "pagination": {
                "page": 0,
                "pageItemCount": 2,
                "totalItems": 4,
                "numberOfPages": 2,
            },
        },
        {
            "virtualCards": [
                {"id": "card3", "displayName": "Test Card 3"},
                {"id": "card4", "displayName": "Test Card 4"},
            ],
            "pagination": {
                "page": 1,
                "pageItemCount": 2,
                "totalItems": 4,
                "numberOfPages": 2,
            },
        },
    ]

    # Create client with mocked session
    session = AsyncMock()
    session.request = AsyncMock()

    responses = mock_responses.copy()

    async def mock_response(*args, **kwargs):
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value=responses.pop(0))
        return response

    session.request.return_value.__aenter__.side_effect = mock_response

    async with AsyncClient(auth, session=session) as client:
        options = ListVirtualCardsOptions(
            pagination_options=PaginationOptions(page=0, count=2),
            cardholder_or_viewer="me",
            issued=True,
            statuses=[VirtualCardStatus.ACTIVE],
        )

        pages = []
        async for page in client.list_virtual_cards(options):
            pages.append(page)

        assert len(pages) == 2
        assert len(pages[0].virtual_cards) == 2
        assert pages[0].virtual_cards[0].id == "card1"
        assert pages[1].virtual_cards[1].id == "card4"
