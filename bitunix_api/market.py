from .http_client import HttpClient
from typing import Dict, Any, Optional

class MarketAPI:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client

    def get_single_trading_pair_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific futures trading pair, including precision details.

        Args:
            symbol: The full symbol of the trading pair (e.g., "BTCUSDT").

        Returns:
            Optional[Dict[str, Any]]: Trading pair information if found, None otherwise.
        """
        path = '/api/v1/futures/market/trading_pairs'
        params = {"symbols": symbol.upper()}
        
        response = self._http_client.get(path, params=params)
        if response and isinstance(response, list) and len(response) > 0:
            return response[0] # The API returns a list, even for a single symbol
        return None