# Extend API

Programmatically manage virtual cards on [Extend](https://www.paywithextend.com/)

> [!CAUTION]
> This is an **unofficial** client that is not affiliated with or endorsed by Extend.
> Using this client may violate Extend's Terms of Service.
> By using this client, you acknowledge and accept all associated risks.

## Installation

```sh
pip install extend-vcc
```

## Device Verification

1. Login to the Extend dashboard
2. Open the browser's developer tools
3. Run the following JavaScript in the console:

```js
function lookup(suffix) {
  const key = Object.keys(localStorage).find(
    (key) =>
      key.startsWith("CognitoIdentityServiceProvider") && key.endsWith(suffix)
  );
  if (!key) return;
  console.log(suffix, localStorage[key]);
}
lookup("deviceGroupKey");
lookup("deviceKey");
lookup("randomPasswordKey");
```

## Quick Start

### Initialize the client

```python
from extend_vcc import Client
from extend_vcc.cognito import Cognito, AuthParams

# Initialize authentication
auth = Cognito(AuthParams(
    username="user@email.com",
    password="password",
    device_group_key="device_group_key",  # deviceGroupKey from browser
    device_key="device_key",  # deviceKey from browser
    device_password="device_password",  # randomPasswordKey from browser
))

# Create client
client = Client(auth)
```

### Create a virtual card

```python
from extend_vcc.virtual_card import CreateVirtualCardOptions
from extend_vcc.types import Currency
from datetime import datetime, timedelta

card = client.create_virtual_card(CreateVirtualCardOptions(
    credit_card_id="cc_id",
    display_name="Team Expenses",
    balance_cents=10000,
    currency=Currency.USD,
    valid_to=datetime.now() + timedelta(days=30),
    recipient="team@company.com",
    notes="This card is for team expenses"
))
```

### Get a virtual card

```python
card = client.get_virtual_card("vc_id")
```

### Cancel a virtual card

```python
card = client.cancel_virtual_card("vc_id")
```

### Close a virtual card

```python
card = client.close_virtual_card("vc_id")
```

### List virtual cards with pagination

```python
from extend_vcc.types import PaginationOptions, SortDirection
from extend_vcc.virtual_card import ListVirtualCardsOptions, VirtualCardStatus

# Create listing options
options = ListVirtualCardsOptions(
    pagination_options=PaginationOptions(
        page=0,
        count=10,
        sort_direction=SortDirection.ASC,
        sort_field="activeClosedUpdatedAt"
    ),
    cardholder_or_viewer="me",
    issued=True,
    statuses=[VirtualCardStatus.ACTIVE]
)

# Get paginator
cards = client.list_virtual_cards(options)

# Iterate through pages
for page in cards:
    for card in page.items():
        # Process each card
        print(f"Card: {card.display_name}")
```

### Bulk create virtual cards

```python
from extend_vcc.virtual_card import BulkCreateVirtualCard, VirtualCardType
from datetime import datetime, timedelta

# Prepare card configurations
cards = [
    BulkCreateVirtualCard(
        card_type=VirtualCardType.STANDARD,
        recipient="user1@company.com",
        display_name="Marketing Card 1",
        balance_cents=10000,
        valid_to=datetime.now() + timedelta(days=30)
    ),
    BulkCreateVirtualCard(
        card_type=VirtualCardType.STANDARD,
        recipient="user2@company.com",
        display_name="Marketing Card 2",
        balance_cents=20000,
        valid_to=datetime.now() + timedelta(days=30)
    )
]

# Create cards in bulk
upload = client.bulk_create_virtual_cards("cc_id", cards)

# Check bulk upload status
status = client.get_bulk_virtual_card_upload(upload.bulk_virtual_card_push.bulk_virtual_card_upload_id)
```

## Contributing

Contributions are welcome! Please see our [contributing guidelines](docs/development.md) for more details.

## License

[MIT](LICENSE)

## Support

For issues, please open a GitHub issue in the repository.

## Credits
This is a python version of the golang package made by [saucesteals](https://github.com/saucesteals) which can be found [here](https://github.com/saucesteals/extend/)