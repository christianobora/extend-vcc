import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from extend_vcc import Client
from extend_vcc.cognito import Cognito
from extend_vcc.types import Currency
from extend_vcc.virtual_card import CreateVirtualCardOptions


class TestClient(unittest.TestCase):
    def setUp(self):
        self.auth = MagicMock(spec=Cognito)
        self.auth.get_access_token.return_value = "test-token"
        self.client = Client(self.auth)

    @patch("requests.Session.request")
    def test_create_virtual_card(self, mock_request):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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
        mock_request.return_value = mock_response

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
        card = self.client.create_virtual_card(options)

        self.assertEqual(card.id, "vc_dummy_id")
        self.assertEqual(card.display_name, "Test Card")
        self.assertEqual(card.balance_cents, 10000)


if __name__ == "__main__":
    unittest.main()
