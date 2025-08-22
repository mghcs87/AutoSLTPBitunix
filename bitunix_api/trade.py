from .http_client import HttpClient
from typing import Dict, Any, Optional, List

class TradeAPI:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client

    def get_symbol_open_orders(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get all open orders for a specific symbol.

        Args:
            symbol: The symbol of the trading pair (e.g., "BTCUSDT").

        Returns:
            List[Dict[str, Any]]: List of open orders.
        """
        path = '/api/v1/futures/trade/get_pending_orders'
        params = {"symbol": symbol.upper()}
        return self._http_client.get(path, params=params)

    def get_symbol_pending_tpsl_orders(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get all pending TP/SL orders for a specific symbol.

        Args:
            symbol: The symbol of the trading pair (e.g., "BTCUSDT").

        Returns:
            List[Dict[str, Any]]: List of pending TP/SL orders.
        """
        path = '/api/v1/futures/tpsl/get_pending_orders'
        params = {"symbol": symbol.upper()}
        return self._http_client.get(path, params=params)

    def cancel_orders(self, symbol: str, order_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Cancel multiple orders.

        Args:
            symbol: Trading pair.
            order_list: List of orders, each containing orderId or clientId.

        Returns:
            Dict[str, Any]: Cancellation result.
        """
        path = '/api/v1/futures/trade/cancel_orders'
        data = {
            "symbol": symbol,
            "orderList": order_list
        }
        return self._http_client.post(path, data)

    def cancel_all_orders(self, symbol: str = None) -> Dict[str, Any]:
        """
        Cancel all open orders, optionally for a specific symbol.

        Args:
            symbol: The symbol of the trading pair (e.g., "BTCUSDT"). If None, cancels all orders for all symbols.

        Returns:
            Dict[str, Any]: Cancellation result.
        """
        path = '/api/v1/futures/trade/cancel_all_orders'
        data = None
        if symbol:
            data = {'symbol': symbol.upper()}
        return self._http_client.post(path, data)

    def place_order(self, symbol: str, side: str, order_type: str, qty: str,
                    trade_side: str,
                    price: Optional[str] = None, position_id: Optional[str] = None,
                    effect: Optional[str] = "GTC", reduce_only: bool = False,
                    client_id: Optional[str] = None,
                    tp_price: Optional[str] = None, tp_stop_type: Optional[str] = None,
                    tp_order_type: Optional[str] = None, tp_order_price: Optional[str] = None,
                    sl_price: Optional[str] = None, sl_stop_type: Optional[str] = None,
                    sl_order_type: Optional[str] = None, sl_order_price: Optional[str] = None) -> Dict[str, Any]:
        """
        Places a new order with extensive options for TP/SL.

        Args:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            side (str): Order direction ('BUY' or 'SELL').
            order_type (str): Order type ('LIMIT' or 'MARKET').
            qty (str): Order quantity.
            trade_side (str): Trade side ('OPEN' or 'CLOSE').
            price (Optional[str]): Order price, required for LIMIT orders.
            position_id (Optional[str]): Position ID, required when trade_side is 'CLOSE'.
            effect (Optional[str]): Order validity ('GTC', 'FOK', 'IOC', 'POST_ONLY'). Defaults to 'GTC'.
            reduce_only (bool): If true, the order will only reduce the position. Defaults to False.
            client_id (Optional[str]): Custom client order ID.
            tp_price (Optional[str]): Take-profit trigger price.
            tp_stop_type (Optional[str]): TP trigger type ('MARK_PRICE' or 'LAST_PRICE').
            tp_order_type (Optional[str]): TP order type ('LIMIT' or 'MARKET').
            tp_order_price (Optional[str]): TP order price (required if tp_order_type is 'LIMIT').
            sl_price (Optional[str]): Stop-loss trigger price.
            sl_stop_type (Optional[str]): SL trigger type ('MARK_PRICE' or 'LAST_PRICE').
            sl_order_type (Optional[str]): SL order type ('LIMIT' or 'MARKET').
            sl_order_price (Optional[str]): SL order price (required if sl_order_type is 'LIMIT').

        Returns:
            Dict[str, Any]: The response from the API containing the order details.
        """
        path = "/api/v1/futures/trade/place_order"
        
        # --- 1. Build the base data payload with required parameters ---
        data = {
            "symbol": symbol,
            "side": side.upper(),
            "orderType": order_type.upper(),
            "qty": qty,
            "tradeSide": trade_side.upper(),
        }

        # --- 2. Add optional parameters to the payload if they are provided ---
        optional_params = {
            "price": price,
            "positionId": position_id,
            "effect": effect,
            "reduceOnly": reduce_only,
            "clientId": client_id,
            "tpPrice": tp_price,
            "tpStopType": tp_stop_type,
            "tpOrderType": tp_order_type,
            "tpOrderPrice": tp_order_price,
            "slPrice": sl_price,
            "slStopType": sl_stop_type,
            "slOrderType": sl_order_type,
            "slOrderPrice": sl_order_price,
        }

        for key, value in optional_params.items():
            if value is not None:
                # Special handling for boolean `reduceOnly`
                if isinstance(value, bool):
                    data[key] = str(value).lower()
                else:
                    data[key] = value
        
        # --- 3. Make the API call ---
        return self._http_client.post(path, data)

    def place_position_tpsl_order(self, symbol: str, position_id: str,
                                  sl_price: Optional[str] = None,
                                  tp_price: Optional[str] = None) -> Dict[str, Any]:
        """
        Place a Take Profit and/or Stop Loss order linked directly to a position.
        When triggered, the entire position is closed using MARK_PRICE.

        Args:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            position_id (str): The ID of the position to attach the TP/SL to.
            sl_price (Optional[str]): The stop-loss trigger price.
            tp_price (Optional[str]): The take-profit trigger price.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        path = "/api/v1/futures/tpsl/position/place_order"
        data = {
            "symbol": symbol,
            "positionId": position_id,
        }
        if sl_price:
            data["slPrice"] = sl_price
        if tp_price:
            data["tpPrice"] = tp_price
            
        return self._http_client.post(path, data)