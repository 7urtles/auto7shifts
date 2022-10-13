import requests
import urllib.parse
import dotsi

from datetime import datetime
from . import verifications as v
import stripe




# -----------------------------------------------------------------------------
def test_verify_7shifts_login():
    test_request = {
        'form' : {
            'email' :' charleshparmley@icloud.com',
            'password' : 'Earthday19!@22'
        }
    }
    test_request = dotsi.Dict(test_request)
    if not v.verify_7shifts_login(test_request):
        return False
    return True


# -----------------------------------------------------------------------------
def test_verify_stripe_payment()->dict|bool:
    stripe.api_key = "sk_test_51LT7lVESVNiUR2k6aelDkD0m3MgdDsvHQjcMWMKcfA28VAjK9WFgAK4Q3Xi3vrh09DXykcjvXsVDNNzFlJkc9ZSW003M5oNf2R"
    payment = stripe.PaymentIntent.create(amount=1000, currency="usd", payment_method="pm_card_visa")
    print(payment)
    return True
