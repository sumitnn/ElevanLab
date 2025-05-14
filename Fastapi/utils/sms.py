import httpx
from fastapi import HTTPException
import os
import stripe
from dotenv import load_dotenv
load_dotenv()

STRIPE_PRODUCT_ID=os.getenv("STRIPE_PRODUCT_ID")
STRIPE_API_KEY=os.getenv("STRIPE_API_KEY")
stripe.api_key = STRIPE_API_KEY

def send_sms(to: str, message:str):
    url = "https://rest.clicksend.com/v3/sms/send"
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {
                "from": os.getenv("CLICKSEND_FROM"),
                "body":message,
                "to": to
            }
        ]
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            auth=(os.getenv("CLICKSEND_USERNAME"), os.getenv("CLICKSEND_API_KEY")),
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            return True
    except Exception as e:
        print(f"SMS sending failed: {str(e)}")
        return False



def create_stripe_payment_link(usdt_amount: int, currency: str = "gbp"):
    try:
        # product = stripe.Product.create(name=product_name)
        price = stripe.Price.create(
            product=STRIPE_PRODUCT_ID,
            unit_amount=gbp_to_pence(usdt_amount),
            currency=currency
        )
        payment_link = stripe.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}]
        )
        return payment_link.url
    except Exception as e:
        print(f"Stripe error: {str(e)}")
        return None
    
def gbp_to_pence(amount: int) -> int:
    return int(amount * 100)

