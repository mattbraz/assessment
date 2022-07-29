"""API Client and basic tests for a secret project."""

import base64
import hashlib
import hmac
import time
import urllib.parse
import requests
from typing import Mapping, MutableMapping, Iterable


class API:
    """Implements a client for a subset of the REST API for ..."""

    def __init__(self, base_url=None, key=None, secret=None, otp=None):
        """Init an instance of the API object.  If you're using the private
            API you must pass the key and secret.

           Args:
               base_url: Required hostname e.g: www.api.com
               key: Optional public key
               secret: Optional private key
               otp: The one time password must be included if 2FA is enabled.

        """
        if base_url is None:
            raise Exception("You must pass the base url")
        self.base_url = base_url
        self.key = key
        self.secret = secret
        self.otp = otp
        self.version = 0

    def _get_signature(self, urlpath: str, data: Mapping) -> str:
        """Return a signature using the url, post data and secret."""
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def _get_private_request(self, action: str, data: MutableMapping) -> requests.Response:
        """Makes a request to the private API. The private API requires a key,
            secret and possibly an otp if you have 2FA enabled.

           Args:
               action: Type of request to make, used to construct the endpoint url.
               data: A dictionary of any parameters required for the request.

           Returns:
               A requests.Response object
        """

        if not self.key or not self.secret:
            raise Exception("You must pass an API key and secret to use the private API")

        data["nonce"] = str(int(1000*time.time()))
        data["otp"] = self.otp

        uri_path = f"/{self.version}/private/{action}"
        uri = f"https://{self.base_url}{uri_path}"
        headers = {
            'User-Agent': 'API Client',
            'API-Key':    self.key,
            'API-Sign':   self._get_signature(uri_path, data)
        }
        return requests.post(uri, headers=headers, data=data)

    def _get_public_request(self, action: str, data: Mapping) -> requests.Response:
        """Makes a request to the public API.

           Args:
               action: Type of request to make, used to construct the endpoint url.
               data: A dictionary of any parameters required for the request.

           Returns:
               A requests.Response object
        """

        data_str = ",".join(f"{k}={v}" for k, v in data.items())
        uri = f"https://{self.base_url}/{self.version}/public/{action}?{data_str}"
        return requests.get(uri)

    def get_server_time(self):
        return self._get_public_request('Time', {})

    def get_asset_pair(self, pair: str) -> requests.Response:
        data = {'pair': pair}
        return self._get_public_request('AssetPairs', data)

    def get_asset_pairs(self, pairs: Iterable[str]) -> requests.Response:
        data = {'pair': ",".join(pairs)}
        return self._get_public_request('AssetPairs', data)

    def get_open_orders(self) -> requests.Response:
        data = {"trades": True}
        return self._get_private_request('OpenOrders', data)



class CommonTests():
    """Implements common functions that can be used to compose tests for
        various testing frameworks like cucumber, unittest, etc.
    """

    FIELDS = {
        'Time':    {
            'rfc1123':  str,
            'unixtime': int,
        },
        'AssetPairs':   dict,
        'AssetPair':    {
            'aclass_base':         str,
            'aclass_quote':        str,
            'altname':             str,
            'base':                str,
            'fee_volume_currency': str,
            'fees':                list,
            'fees_maker':          list,
            'leverage_buy':        list,
            'leverage_sell':       list,
            'lot':                 str,
            'lot_decimals':        int,
            'lot_multiplier':      int,
            'margin_call':         int,
            'margin_stop':         int,
            'ordermin':            str,
            'pair_decimals':       int,
            'quote':               str,
            'wsname':              str
        },
        'OpenOrders':    {
            'open': dict,
        },
        'Order':    {
            'refid':      str,
            'userref':    str,
            'status':     str,
            'opentm':     int,
            'starttm':    int,
            'expiretm':   int,
            'descr':      dict,
            'vol':        str,
            'vol_exec':   str,
            'cost':       str,
            'fee':        str,
            'price':      str,
            'stopprice':  str,
            'limitprice': str,
            'trigger':    str,
            'misc':       str,
            'oflags':     str,
            'trades':     list
        }
    }

    @staticmethod
    def http_checks(resp: requests.Response):
        """Basic http checks for a successful request."""
        # Check it's a valid http response code.
        # (todo: this could be different for some requests)
        assert resp.status_code == 200
        # Check various header values
        assert resp.headers['Content-Type'] == 'application/json'
        # Check various headers are present
        for h in ['Date', 'Connection', 'referrer-policy']:
            assert h in resp.headers, f"{h} not in headers"
        # Check certain data is not leaked in headers
        assert 'X-Powered-By' not in resp.headers
        # Check encoding
        assert resp.encoding == 'utf-8'

    @staticmethod
    def basic_api_checks(resp: requests.Response):
        """Basic api checks for a successful request."""
        data = resp.json()
        assert 'error' in data
        assert data['error'] == []
        assert 'result' in data

    @staticmethod
    def _check_fields(data, fields_spec):
        """Check the population and data-type of the expected fields according
            to a specification.
        """
        fields = fields_spec.copy()
        for field, field_data in data.items():
            assert field in fields, f"unchecked field in response: {field}"
            assert isinstance(field_data, fields[field]), f"{field} has type {type(field_data)} expected {fields[field]}"
            del fields[field]
        assert fields == {}, f"There are missing fields in the response: {list(fields.keys())}"

    @classmethod
    def check_fields_server_time(cls, resp: requests.Response):
        cls._check_fields(resp.json()['result'], cls.FIELDS.get('Time', {}))

    @classmethod
    def check_fields_asset_pairs(cls, resp: requests.Response):
        assert isinstance(resp.json()['result'], dict)
        for name, asset in resp.json()['result'].items():
            cls._check_fields(asset, cls.FIELDS['AssetPair'])

    @classmethod
    def check_fields_open_orders(cls, resp: requests.Response):
        cls._check_fields(resp.json()['result'], cls.FIELDS['OpenOrders'])
        for txid, order in resp.json()['result']['open'].items():
            cls._check_fields(order, cls.FIELDS['Order'])
