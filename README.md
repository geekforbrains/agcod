# Amazon Gift Code On-Demand (AGCOD)

This is a tool for working with the AGCOD service and can be used for easily created, cancelling
and checking the status of Amazon gift codes.


## Install

`pip install agcod`


## Quickstart

```python
from agcod import client

client.debug = True
client.partner_id = '<Your Partner ID>'
client.aws_key_id = '<Your AWS Key ID>'
client.aws_secret_key = '<Your AWS Secret Key>'
client.aws_region_name = '<Your AWS Region>'

# Request ID must begin with Partner ID
request_id = client.partner_id + 'EXAMPLE'
amount = 1.00
currency = 'USD'

# Create a new gift code
result = client.create_gift_card(request_id, amount, currency)

# Example response
# {
#   "cardInfo": {
#     "cardNumber": null,
#     "cardStatus": "Fulfilled",
#     "expirationDate": null,
#     "value": {
#       "amount": 1.0,
#       "currencyCode": "USD"
#     }
#   },
#   "creationRequestId": "MyidEXAMPLE",
#   "gcClaimCode": "ABCD-12345-WXYZ",
#   "gcExpirationDate": null,
#   "gcId": "AA11BB22CC33DD",
#   "status": "SUCCESS"
# }

# Cancel that gift code
client.cancel_gift_card(request_id, result['gcId'])
```