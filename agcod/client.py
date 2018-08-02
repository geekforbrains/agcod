import binascii
import hashlib
import hmac
import json
from datetime import datetime
from time import time

import requests


# Constants
AWS_SERVICE_NAME = 'AGCODService'
AWS_SHA256_ALGORITHM = 'AWS4-HMAC-SHA256'
AWS_TERMINATION_STRING = "aws4_request"
AWS_KEY_QUALIFER = 'AWS4'

HOST = 'agcod-v2-gamma.amazon.com'
BASE_URL = 'https://' + HOST

DATE_FORMAT = '%Y%m%dT%H%M%SZ'
DATE_TIMEZONE = 'UTC'


# Configs
debug = False
partner_id = None
aws_key_id = None
aws_secret_key = None
aws_region_name = 'us-east-1'


def _debug(title, data):
    if debug:
        print(title.center(50, '-'))
        print(data)
        print()


def _hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _hmac_binary(data, bkey):
    bkey = bkey.encode('utf-8') if isinstance(bkey, str) else bkey
    data = data.encode('utf-8') if isinstance(data, str) else data
    return hmac.new(bkey, data, hashlib.sha256).digest()


def _build_derived_key(date_string):
    aws_key_signature = AWS_KEY_QUALIFER + aws_secret_key
    key_date = _hmac_binary(date_string, aws_key_signature)
    key_region = _hmac_binary(aws_region_name, key_date)
    key_service = _hmac_binary(AWS_SERVICE_NAME, key_region)
    key_signing = _hmac_binary(AWS_TERMINATION_STRING, key_service)
    derived_key = key_signing.hex()

    _debug('DERIVED SIGNING KEY', derived_key)

    return key_signing


def _build_canonical_request(operation, payload, headers):
    header_keys = []
    hashed_payload = _hash(json.dumps(payload))

    _debug('HASHED PAYLOAD', hashed_payload)

    canonical_request = ['POST', "/{0}\n".format(operation)]

    for k, v in headers.items():
        header_keys.append(k)
        canonical_request.append('{0}:{1}'.format(k, v))

    canonical_request.append("\n" + ';'.join(header_keys))
    canonical_request.append(hashed_payload)

    resp = "\n".join(canonical_request)

    _debug('CANONICAL REQUEST', resp)

    return _hash(resp)


def _build_signing_string(headers, canonical_request_hash, date_string):
    signing_string = "\n".join([
        AWS_SHA256_ALGORITHM,
        headers['x-amz-date'],
        '/'.join([date_string, aws_region_name, AWS_SERVICE_NAME, AWS_TERMINATION_STRING]),
        canonical_request_hash
    ])

    _debug('STRING TO SIGN', signing_string)

    return signing_string


def _build_auth_signature(signing_string, date_string):
    derived_key = _build_derived_key(date_string)
    final_signature = _hmac_binary(signing_string, derived_key)
    signature = binascii.hexlify(final_signature).decode('utf-8')

    _debug('SIGNATURE', signature)

    auth_sig = ''.join([
        AWS_SHA256_ALGORITHM,
        ' Credential={0}/'.format(aws_key_id),
        '{0}/'.format(date_string),
        '{0}/'.format(aws_region_name),
        '{0}/'.format(AWS_SERVICE_NAME),
        '{0},'.format(AWS_TERMINATION_STRING),
        ' SignedHeaders=accept;content-type;host;x-amz-date;x-amz-target,',
        ' Signature={0}'.format(signature)
    ])

    _debug('AUTH SIGNATURE', auth_sig)

    return auth_sig


def _get_auth_header(operation, payload, headers):
    date_string = headers['x-amz-date'][0:8]
    canonical_request_hash = _build_canonical_request(operation, payload, headers)

    _debug('HASHED CANONICAL REQUEST', canonical_request_hash)

    signing_string = _build_signing_string(headers, canonical_request_hash, date_string)
    auth_signature = _build_auth_signature(signing_string, date_string)
    return auth_signature


def _make_request(operation, payload):
    url = BASE_URL + '/' + operation
    timestamp = datetime.utcnow().strftime(DATE_FORMAT)
    target = 'com.amazonaws.agcod.AGCODService.' + operation

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'host': HOST,
        'x-amz-date': timestamp,
        'x-amz-target': target,
    }

    headers['authorization'] = _get_auth_header(operation, payload, headers)

    _debug('PAYLOAD', payload)
    _debug('HEADERS', headers)

    res = requests.post(url, json=payload, headers=headers)
    data = res.json()

    _debug('RESULT', data)

    return data


def get_available_funds():
    return _make_request('GetAvailableFunds', {'partnerId': partner_id})


def create_gift_card(request_id, amount, currency):
    return _make_request('CreateGiftCard', {
        'creationRequestId': request_id,
        'partnerId': partner_id,
        'value': {
            'currencyCode': currency,
            'amount': amount,
        },
    })


def cancel_gift_card(request_id, gc_id):
    return _make_request('CancelGiftCard', {
        'creationRequestId': request_id,
        'partnerId': partner_id,
        'gcId': gc_id,
    })
