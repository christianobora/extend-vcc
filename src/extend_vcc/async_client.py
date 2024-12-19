import json
from typing import Any, AsyncIterator, Dict, List, Optional

import aiohttp

from .auth import Authenticator
from .client import DEFAULT_BRAND, APIError, ExtendPlatformBrand
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


class AsyncClient:
    """
    Async client for the Extend API

    Args:
        auth: Authenticator instance for handling API authentication
        brand: Optional brand configuration (defaults to DEFAULT_BRAND)
        session: Optional aiohttp.ClientSession instance
    """

    def __init__(
        self,
        auth: Authenticator,
        brand: ExtendPlatformBrand = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.auth = auth
        self.brand = brand or DEFAULT_BRAND
        self._session = session
        self._owned_session = session is None

    async def __aenter__(self):
        if self._owned_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owned_session and self._session:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the current session or create a new one"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def request(
        self, method: str, path: str, content_type: str = None, data: Any = None
    ) -> Dict:
        """
        Make an async API request

        Args:
            method: HTTP method
            path: API endpoint path
            content_type: Optional content type header
            data: Optional request data

        Returns:
            Dict containing the response data

        Raises:
            APIError: If the API returns an error response
            aiohttp.ClientError: For network/request errors
        """
        url = f"{self.brand.api_base_url}{path}"

        headers = self.brand.headers.copy()
        headers["Authorization"] = f"Bearer {await self.auth.get_access_token()}"
        headers["Accept"] = "application/vnd.paywithextend.v2021-03-12+json"

        if content_type:
            headers["Content-Type"] = content_type

        async with self.session.request(
            method=method,
            url=url,
            headers=headers,
            data=data if content_type else None,
            json=data if not content_type else None,
        ) as response:
            if not 200 <= response.status <= 299:
                try:
                    error_data = await response.json()
                    raise APIError(
                        message=error_data.get("error", "Unknown error"),
                        details=error_data.get("details", []),
                    )
                except json.JSONDecodeError:
                    response.raise_for_status()

            if response.content_length == 0:
                return None

            return await response.json()

    async def json_request(self, method: str, path: str, data: Any = None) -> Dict:
        """
        Make an async JSON API request
        """
        return await self.request(method, path, "application/json", data)

    # Virtual Card Methods
    async def create_virtual_card(
        self, options: CreateVirtualCardOptions
    ) -> VirtualCard:
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

        response = await self.json_request("POST", "/virtualcards", payload)
        return VirtualCardResponse.from_dict(response).virtual_card

    async def update_virtual_card(
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

        response = await self.json_request("PUT", f"/virtualcards/{card_id}", payload)
        return VirtualCardResponse.from_dict(response).virtual_card

    async def get_virtual_card(self, card_id: str) -> VirtualCard:
        """Get details of a specific virtual card"""
        response = await self.json_request("GET", f"/virtualcards/{card_id}")
        return VirtualCardResponse.from_dict(response).virtual_card

    async def cancel_virtual_card(self, card_id: str) -> VirtualCard:
        """Cancel a virtual card"""
        response = await self.json_request("PUT", f"/virtualcards/{card_id}/cancel")
        return VirtualCardResponse.from_dict(response).virtual_card

    async def close_virtual_card(self, card_id: str) -> VirtualCard:
        """Close a virtual card"""
        response = await self.json_request("PUT", f"/virtualcards/{card_id}/close")
        return VirtualCardResponse.from_dict(response).virtual_card

    async def list_virtual_cards(
        self, options: ListVirtualCardsOptions
    ) -> AsyncIterator[ListVirtualCardsResponse]:
        """
        List virtual cards with pagination
        Returns an async iterator over pages of virtual cards
        """
        query = {
            "page": str(options.pagination_options.page),
            "count": str(options.pagination_options.count),
            "sortDirection": options.pagination_options.sort_direction.value,
            "sortField": options.pagination_options.sort_field,
            "cardholderOrViewer": options.cardholder_or_viewer,
            "issued": str(options.issued).lower(),
            "statuses": ",".join(status.value for status in options.statuses),
        }

        while True:
            response = await self.json_request(
                "GET", f"/virtualcards?{'&'.join(f'{k}={v}' for k, v in query.items())}"
            )

            result = ListVirtualCardsResponse(**response)
            yield result

            if result.pagination.page >= result.pagination.number_of_pages - 1:
                break

            query["page"] = str(int(query["page"]) + 1)

    async def bulk_create_virtual_cards(
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

        # Create FormData
        form = aiohttp.FormData()
        form.add_field(
            "file",
            output.getvalue(),
            filename="virtual_cards.csv",
            content_type="text/csv",
        )

        response = await self.request(
            "POST", f"/creditcards/{credit_card_id}/bulkvirtualcardpush", data=form
        )
        return BulkVirtualCardPushResponse.from_dict(response)

    async def get_bulk_virtual_card_upload(
        self, upload_id: str
    ) -> BulkVirtualCardUpload:
        """Get status of a bulk virtual card upload"""
        response = await self.json_request(
            "GET", f"/bulkvirtualcarduploads/{upload_id}"
        )
        return response["bulkVirtualCardUpload"]
