from twilio.rest import Client
from app.registration import reg_env



client = Client(reg_env.TWILIO_ACCOUNT_SID, reg_env.TWILIO_AUTH_TOKEN)


def send_verification_code(email):
    verification = client.verify.services(
        reg_env.TWILIO_VERIFY_SERVICE).verifications.create(
            to=email, channel='email')
    assert verification.status == 'pending'



def check_verification_code(email, code):
    verification = client.verify.services(
        reg_env.TWILIO_VERIFY_SERVICE).verification_checks.create(
            to=email, code=code)
    return verification.status == 'approved'