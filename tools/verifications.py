import requests
import urllib.parse
import dotsi
from datetime import datetime
import stripe
# Special characters need to be translated to their url equivelant....



url = "https://app.7shifts.com/users/login"
headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Origin': 'null',
  'Alt-Used': 'app.7shifts.com',
  'Connection': 'keep-alive',
  'Cookie': '',
  'Upgrade-Insecure-Requests': '1',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'cross-site',
  'Sec-Fetch-User': '?1',
  'TE': 'trailers',
  'Authorization': 'Basic Y2hhcmxlc2hwYXJtbGV5QGljbG91ZC5jb206RWFydGhkYXkxOSFAMjI='
}


# -----------------------------------------------------------------------------
def verify_7shifts_login(request:dict)->dict|bool:
    login_credentials = dict(request.form)

    email = urllib.parse.quote(login_credentials['email'])
    password = urllib.parse.quote(login_credentials['password'])

    payload=f"_method=POST&data%5B_Token%5D%5Bkey%5D=e64e3e0f5839c297289c3dda1fa2ca7d&data%5BUser%5D%5Bemail%5D={email}&data%5BUser%5D%5Bpassword%5D={password}&data%5BUser%5D%5Bredirect%5D=&data%5BUser%5D%5Bkeep_me_logged_in%5D=0&data%5BUser%5D%5Bkeep_me_logged_in%5D=1&submit=Login&data%5B_Token%5D%5Bfields%5D=be4fd85121b5dd0aea168db08ad7a5daf34c830b%253AUser.redirect&data%5B_Token%5D%5Bunlocked%5D="
    
    # Send constructed login request to 7shifts.com
    response = requests.request("POST", url, headers=headers, data=payload)
    
    # Check response url to see if login suceeded.
    # If login request fails 7shifts.com redirects to --> https://app.7shifts.com/users/login
    if response.url == "https://app.7shifts.com/employees":
        login_credentials.update({
            'time_submitted':datetime.now(), 
            "login_success":True
        })
        return login_credentials
    return False



# -----------------------------------------------------------------------------
def verify_stripe_payment(request:dict,END_KEY:str)->dict|bool:
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, END_KEY
            )
    except ValueError as e:
        # Invalid payload
        raise e

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        print(event)
        payment_email = event['data']['object']['charges']['data'][0]['billing_details']['email']
        print('payment succeeded')
        return payment_intent        
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event['type']))
        return False