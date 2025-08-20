from .http_client import HttpClient
from typing import Dict, Any, Optional

class AccountAPI:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client

    def get_symbol_open_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get information about open positions for a specific symbol.

        Args:
            symbol: The symbol of the trading pair (e.g., "BTCUSDT").

        Returns:
            Optional[Dict[str, Any]]: Position information if found, None otherwise.
        """
        path = '/api/v1/futures/position/get_pending_positions'
        params = {"symbol": symbol.upper()}
        
        response = self._http_client.get(path, params=params)
        if response and isinstance(response, list) and len(response) > 0:
            return response[0]
        return None
