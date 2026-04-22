import hmac
import hashlib
import time
import logging
import requests
from urllib.parse import urlencode

logger = logging.getLogger("trading_bot")

class APIError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        
    def __str__(self):
        return f"APIError {self.status_code}: {self.message}"

class NetworkError(Exception):
    pass

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://demo-fapi.binance.com"
        
    def _sign_request(self, params: dict) -> dict:
        # Add timestamp
        params['timestamp'] = int(time.time() * 1000)
            
        # Create query string
        query_string = urlencode(params)
        
        # Generate signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        signed_params = params.copy()
        signed_params['signature'] = signature
        return signed_params

    def _post(self, endpoint: str, params: dict) -> dict:
        signed_params = self._sign_request(params)
        url = f"{self.base_url}{endpoint}"
        headers = {
            "X-MBX-APIKEY": self.api_key
        }
        
        logger.debug(f"POST request to {endpoint} | params args: {signed_params}")
        
        try:
            response = requests.post(url, headers=headers, params=signed_params)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error occurred: {e}") from e
            
        logger.debug(f"POST response from {endpoint} | Status: {response.status_code} | Body: {response.text}")
        
        if response.status_code != 200:
            error_message = response.text
            try:
                # Attempt to extract Binance error message if JSON is present
                json_err = response.json()
                if "msg" in json_err:
                    error_message = json_err["msg"]
            except ValueError:
                pass
                
            raise APIError(error_message, response.status_code)
            
        return response.json()
