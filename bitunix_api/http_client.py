import hashlib
import time
from typing import Dict, Any, Optional
import uuid
import requests
import json

from bitunix_api.config import Config
from bitunix_api.error_codes import ErrorCode

def get_nonce() -> str:
    """
    Generate a random string as nonce
    
    Returns:
        str: 32-character random string
    """
    return str(uuid.uuid4()).replace('-', '')

def get_timestamp() -> str:
    """
    Get current timestamp in milliseconds
    
    Returns:
        str: Millisecond timestamp
    """
    return str(int(time.time() * 1000))

def generate_signature(
    api_key: str,
    secret_key: str,
    nonce: str,
    timestamp: str,
    query_params: str = "",
    body: str = ""
) -> str:
    """
    Generate signature according to Bitunix OpenAPI doc
    Args:
        api_key: API key
        secret_key: Secret key
        nonce: Random string
        timestamp: Timestamp
        query_params: Sorted query string (no spaces)
        body: Raw JSON string (no spaces)
    Returns:
        str: Signature
    """
    digest_input = nonce + timestamp + api_key + query_params + body
    digest = hashlib.sha256(digest_input.encode('utf-8')).hexdigest()
    sign_input = digest + secret_key
    sign = hashlib.sha256(sign_input.encode('utf-8')).hexdigest()
    return sign

def get_auth_headers(
    api_key: str,
    secret_key: str,
    query_params: str = "",
    body: str = ""
) -> Dict[str, str]:
    """
    Get authentication headers
    
    Args:
        api_key: API key
        secret_key: Secret key
        query_params: Query parameters
        body: Request body
        
    Returns:
        Dict[str, str]: Authentication headers
    """
    nonce = get_nonce()
    timestamp = get_timestamp()
    
    sign = generate_signature(
        api_key=api_key,
        secret_key=secret_key,
        nonce=nonce,
        timestamp=timestamp,
        query_params=query_params,
        body=body
    )
    
    return {
        "api-key": api_key,
        "sign": sign,
        "nonce": nonce,
        "timestamp": timestamp
    }

def sort_params(params: Dict[str, str]) -> str:
    """
    Sort parameters and concatenate them
    
    Args:
        params: Parameter dictionary
        
    Returns:
        str: Sorted parameter string
    """
    if not params:
        return ""
        
    # Sort by key and concatenate directly
    return ''.join(f"{k}{v}" for k, v in sorted(params.items()))

class HttpClient:
    def __init__(self, config: Config):
        """
        Initialize HttpClient class
        
        Args:
            config: Configuration object containing api_key and secret_key
        """
        self.config = config
        self.api_key = config.api_key
        self.secret_key = config.secret_key
        self.base_url = config.uri_prefix
        self.session = requests.Session()
        
        # Set common request headers
        self.session.headers.update({
            "language": "en-US",
            "Content-Type": "application/json"
        })
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle response
        
        Args:
            response: Response object
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            Exception: When response status code is not 200 or business status code is not 0
        """
        if response.status_code != 200:
            raise Exception(f"HTTP Error: {response.status_code}")
        
        data = response.json()
        if data["code"] != 0:
            error = ErrorCode.get_by_code(data["code"])
            if error:
                raise Exception(str(error))
            raise Exception(f"Unknown Error: {data['code']} - {data['msg']}")
        
        return data["data"]

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        query_string = sort_params(params) if params else ""
        headers = get_auth_headers(self.api_key, self.secret_key, query_params=query_string)
        response = self.session.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        request_data = data if data is not None else {}
        body = json.dumps(request_data)
        headers = get_auth_headers(self.api_key, self.secret_key, body=body)
        response = self.session.post(url, json=request_data, headers=headers)
        return self._handle_response(response)
