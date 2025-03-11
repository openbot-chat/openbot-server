import xpay
from config import PAYMENT_API_KEY, PAYMENT_BASE_URL

xpay.log = 'debug'
xpay.api_key = PAYMENT_API_KEY

if PAYMENT_BASE_URL:
    xpay.api_base = PAYMENT_BASE_URL
