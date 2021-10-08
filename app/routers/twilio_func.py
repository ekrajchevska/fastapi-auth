from twilio.rest import Client
from app.read_env import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE

# from dotenv import load_dotenv

# load_dotenv()

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_verification_code(email):
    verification = client.verify.services(TWILIO_VERIFY_SERVICE).verifications.create(
        to=email, channel="email"
    )
    assert verification.status == "pending"


def check_verification_code(email, code):
    verification = client.verify.services(
        TWILIO_VERIFY_SERVICE
    ).verification_checks.create(to=email, code=code)
    return verification.status == "approved"
