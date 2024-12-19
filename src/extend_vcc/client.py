import json
from typing import Any, Dict, List, Optional

import requests

from .auth import Authenticator
from .base import DEFAULT_BRAND, APIError, ExtendPlatformBrand
from .pagination import Paginator
from .virtual_card import (
    BulkCreateVirtualCard,
    BulkVirtualCardPushResponse,
    BulkVirtualCardUpload,
    CreateVirtualCardOptions,
    ListVirtualCardsOptions,
    ListVirtualCardsResponse,
    UpdateVirtualCardOptions,
    VirtualCard,
    VirtualCardResponse,
)


class Client:
    """
    Extend API client

    Args:
        auth: Authenticator instance for handling API authentication
        brand: Optional brand configuration (defaults to DEFAULT_BRAND)
        session: Optional requests.Session instance
    """

    def __init__(
        self,
        auth: Authenticator,
        brand: Optional[ExtendPlatformBrand] = None,
        session: Optional[requests.Session] = None,
    ):
        self.auth = auth
        self.brand = brand or DEFAULT_BRAND
        self.session = session or requests.Session()

    def request(
        self, method: str, path: str, content_type: str = None, data: Any = None
    ) -> Dict:
        """
        Make an API request

        Args:
            method: HTTP method
            path: API endpoint path
            content_type: Optional content type header
            data: Optional request data

        Returns:
            Dict containing the response data

        Raises:
            APIError: If the API returns an error response
            requests.RequestException: For network/request errors
        """
        try:
            url = f"{self.brand.api_base_url}{path}"

            headers = self.brand.headers.copy()
            headers["Authorization"] = f"Bearer {self.auth.get_access_token()}"
            headers["Accept"] = "application/vnd.paywithextend.v2021-03-12+json"

            if content_type:
                headers["Content-Type"] = content_type

            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data if content_type != "application/json" else None,
                json=data if content_type == "application/json" else None,
            )

            if not 200 <= response.status_code < 300:
                try:
                    error_data = response.json()
                    raise APIError(
                        message=error_data.get("error", "Unknown error"),
                        details=error_data.get("details", []),
                    )
                except json.JSONDecodeError:
                    response.raise_for_status()

            if not response.content:
                return None

            return response.json()
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()
            raise APIError("Request error", [str(e)])

    def json_request(self, method: str, path: str, data: Any = None) -> Dict:
        """
        Make a JSON API request

        Args:
            method: HTTP method
            path: API endpoint path
            data: Optional JSON data

        Returns:
            Dict containing the response data
        """
        return self.request(method, path, "application/json", data)

    def create_virtual_card(self, options: CreateVirtualCardOptions) -> VirtualCard:
        """Create a new virtual card"""
        payload = {
            "creditCardId": options.credit_card_id,
            "displayName": options.display_name,
            "balanceCents": options.balance_cents,
            "currency": options.currency.value,
            "validTo": options.valid_to.strftime("%Y-%m-%d"),
            "recipient": options.recipient,
            "notes": options.notes,
        }

        response = self.json_request("POST", "/virtualcards", payload)
        return VirtualCardResponse.from_dict(response).virtual_card

    def update_virtual_card(
        self, card_id: str, options: UpdateVirtualCardOptions
    ) -> VirtualCard:
        """Update an existing virtual card"""
        payload = {
            "creditCardId": options.credit_card_id,
            "displayName": options.display_name,
            "balanceCents": options.balance_cents,
            "recurs": options.recurs,
            "validTo": options.valid_to.strftime("%Y-%m-%d"),
            "currency": options.currency.value,
            "receiptRulesExempt": options.receipt_rules_exempt,
        }

        response = self.json_request("PUT", f"/virtualcards/{card_id}", payload)
        return VirtualCardResponse.from_dict(response).virtual_card

    def get_virtual_card(self, card_id: str) -> VirtualCard:
        """Get details of a specific virtual card"""
        response = self.json_request("GET", f"/virtualcards/{card_id}")
        return VirtualCardResponse.from_dict(response).virtual_card

    def cancel_virtual_card(self, card_id: str) -> VirtualCard:
        """Cancel a virtual card"""
        response = self.json_request("PUT", f"/virtualcards/{card_id}/cancel")
        return VirtualCardResponse.from_dict(response).virtual_card

    def close_virtual_card(self, card_id: str) -> VirtualCard:
        """Close a virtual card"""
        response = self.json_request("PUT", f"/virtualcards/{card_id}/close")
        return VirtualCardResponse.from_dict(response).virtual_card

    def list_virtual_cards(
        self, options: ListVirtualCardsOptions
    ) -> Paginator[VirtualCard, ListVirtualCardsResponse]:
        """List virtual cards with pagination"""
        query = {
            "cardholderOrViewer": [options.cardholder_or_viewer],
            "issued": [str(options.issued).lower()],
            "statuses": [",".join(status.value for status in options.statuses)],
        }

        return Paginator[VirtualCard, ListVirtualCardsResponse](
            self, options.pagination_options, "/virtualcards", query
        )

    def bulk_create_virtual_cards(
        self, credit_card_id: str, cards: List[BulkCreateVirtualCard]
    ) -> BulkVirtualCardPushResponse:
        """Create multiple virtual cards in bulk"""
        import csv
        import io

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Write header
        writer.writerow(
            [
                "Card Type",
                "en-US",
                "Virtual Card User Email",
                "Card Name",
                "Credit Limit",
                "Active Until Date (MM/DD/YYYY)",
                "Notes",
            ]
        )

        # Write card data
        for card in cards:
            writer.writerow(
                [
                    card.card_type.value,
                    "en-US",
                    card.recipient,
                    card.display_name,
                    f"{float(card.balance_cents)/100:.2f}",
                    card.valid_to.strftime("%m/%d/%Y"),
                    card.notes,
                ]
            )

        # Create multipart form data
        files = {"file": ("virtual_cards.csv", output.getvalue(), "text/csv")}

        response = self.request(
            "POST", f"/creditcards/{credit_card_id}/bulkvirtualcardpush", data=files
        )
        return BulkVirtualCardPushResponse(**response)

    def get_bulk_virtual_card_upload(self, upload_id: str) -> BulkVirtualCardUpload:
        """Get status of a bulk virtual card upload"""
        response = self.json_request("GET", f"/bulkvirtualcarduploads/{upload_id}")
        return response["bulkVirtualCardUpload"]
