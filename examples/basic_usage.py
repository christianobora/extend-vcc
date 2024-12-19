from extend_vcc import Client
from extend_vcc.cognito import Cognito, AuthParams
from extend_vcc.virtual_card import CreateVirtualCardOptions
from extend_vcc.types import Currency
from datetime import datetime, timedelta
import random

def main():
    # Initialize authentication
    auth = Cognito(AuthParams(
        username="user@email.com",
        password="password",
        device_group_key="device_group_key",
        device_key="device_key",
        device_password="device_password",
    ))

    # Create client
    client = Client(auth)

    try:
        # Create a virtual card
        card = client.create_virtual_card(CreateVirtualCardOptions(
            credit_card_id="cc_id",
            display_name="Test Card",
            balance_cents=100,
            currency=Currency.USD,
            valid_to=datetime.now() + timedelta(days=30),
            recipient="recipient@company.com",
            notes="Test card creation"
        ))
        
        print(f"Created card: {card.id}")

        # Get card details
        card_details = client.get_virtual_card(card.id)
        print(f"Card balance: ${card_details.balance_cents/100:.2f}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    main()