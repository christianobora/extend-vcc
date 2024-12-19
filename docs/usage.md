# Usage Guide

This guide provides detailed examples for using the Extend API Python client.

## Authentication

```python
from extend_vcc import Client
from extend_vcc.cognito import Cognito, AuthParams

# Set up authentication
auth = Cognito(AuthParams(
    username="user@email.com",
    password="password",
    device_group_key="device_group_key",
    device_key="device_key",
    device_password="device_password"
))

# Initialize client
client = Client(auth)
```

## Managing Virtual Cards

### Creating Cards

```python
from extend_vcc.virtual_card import CreateVirtualCardOptions
from extend_vcc.types import Currency
from datetime import datetime, timedelta

# Create a single card
card = client.create_virtual_card(CreateVirtualCardOptions(
    credit_card_id="cc_id",
    display_name="Marketing Expenses",
    balance_cents=10000,  # $100.00
    currency=Currency.USD,
    valid_to=datetime.now() + timedelta(days=30),
    recipient="marketing@company.com",
    notes="Marketing team expenses"
))

# Bulk create cards
cards = [
    BulkCreateVirtualCard(
        card_type=VirtualCardType.STANDARD,
        recipient="user1@company.com",
        display_name="Card 1",
        balance_cents=5000,
        valid_to=datetime.now() + timedelta(days=30)
    ),
    # Add more cards...
]

result = client.bulk_create_virtual_cards("cc_id", cards)
```

### Card Management

```python
# Get card details
card = client.get_virtual_card("vc_id")

# Update card
updated_card = client.update_virtual_card("vc_id", UpdateVirtualCardOptions(
    credit_card_id="cc_id",
    display_name="New Name",
    balance_cents=20000,
    currency=Currency.USD,
    valid_to=datetime.now() + timedelta(days=60),
    recurs=False,
    receipt_rules_exempt=False
))

# Cancel card
cancelled_card = client.cancel_virtual_card("vc_id")

# Close card
closed_card = client.close_virtual_card("vc_id")
```

### Listing Cards

```python
from extend_vcc.types import PaginationOptions, SortDirection
from extend_vcc.virtual_card import ListVirtualCardsOptions, VirtualCardStatus

# Create listing options
options = ListVirtualCardsOptions(
    pagination_options=PaginationOptions(
        page=0,
        count=10,
        sort_direction=SortDirection.ASC,
        sort_field="createdAt"
    ),
    cardholder_or_viewer="me",
    issued=True,
    statuses=[VirtualCardStatus.ACTIVE]
)

# List cards with pagination
for page in client.list_virtual_cards(options):
    for card in page.items():
        print(f"Card: {card.display_name}")
```

## Error Handling

```python
try:
    card = client.create_virtual_card(options)
except APIError as e:
    print(f"API Error: {e}")
    for detail in e.details:
        print(f"Field: {detail['field']}, Error: {detail['error']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Custom HTTP Client

```python
import requests

session = requests.Session()
session.verify = False  # Disable SSL verification (not recommended)
session.timeout = 30    # Set custom timeout

client = Client(auth)
client.set_http_client(session)
```

### Async Support

```python
import asyncio
from extend_vcc.async_client import AsyncClient

async def main():
    client = AsyncClient(auth)
    card = await client.get_virtual_card("vc_id")
    print(f"Card balance: ${card.balance_cents/100:.2f}")

asyncio.run(main())