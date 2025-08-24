# -*- coding: utf-8 -*- 
# Script for Stop-Loss and Take-Profit automation in Bitunix. 

import time
from bitunix_api.client import BitunixAPI
from decimal import Decimal, ROUND_DOWN

# ============================================================================== 
# INITIAL API CLIENT 
# ============================================================================== 
# HTTP client with the credentials. 
try: 
    session = BitunixAPI() 
except Exception as e: 
    print(f"Fatal error initializing configuration or API client: {e}") 
    exit() 

# ============================================================================== 
# GLOBAL STATE VARIABLES 
# ============================================================================== 
# These variables control the bot's flow: 
symbol = '' 
stop_loss_usd = 0 
is_active = False 
tracked_position_value = 0 
is_tp_active = False 
tp_percentage = 0.0 

# ============================================================================== 
# AUXILIARY FUNCTIONS 
# ============================================================================== 

def adjust_price_to_precision(symbol, price): 
    """
    Adjusts a price to the precision required by the exchange for a specific symbol.
    This is CRITICAL to prevent orders from being rejected.
    1. Fetches instrument information from the API.
    2. Extracts 'quotePrecision' (e.g., 4) and calculates the 'tickSize' (e.g., 0.0001).
    3. Uses the Decimal library to round the price DOWN to the nearest multiple of the 'tickSize'.
    """
    try: 
        instrument_info = session.market.get_single_trading_pair_info(symbol=symbol) 
        if not instrument_info: 
            print(f"Could not retrieve instrument info for {symbol}.") 
            return price 

        quote_precision = instrument_info.get('quotePrecision') 
        if quote_precision is None: 
            print(f"'quotePrecision' not found in instrument info for {symbol}.") 
            return price 

        # Calculate tick_size from quote_precision (e.g., 4 -> 0.0001)
        tick_size = 10 ** -int(quote_precision)

        price_decimal = Decimal(str(price)) 
        tick_size_decimal = Decimal(str(tick_size)) 
        
        adjusted_price = (price_decimal / tick_size_decimal).quantize(Decimal('1'), rounding=ROUND_DOWN) * tick_size_decimal 
        
        return float(adjusted_price) 
        
    except Exception as e: 
        print(f"Error adjusting price precision for {symbol}: {e}") 
        return price 

# ============================================================================== 
# CORE TRADING FUNCTIONS 
# ============================================================================== 

def cancel_existing_tpsl_orders(symbol): 
    """
    Finds and cancels all existing TP/SL orders for a given symbol.
    This is crucial to prevent multiple stop-losses and to replace old ones.
    It works by first fetching all pending TP/SL orders and then canceling them by ID.
    """
    try: 
        pending_orders = session.trade.get_symbol_pending_tpsl_orders(symbol=symbol) 
        
        if pending_orders: 
            orders_to_cancel = [{'orderId': order['id']} for order in pending_orders] 
            print(f"Found {len(orders_to_cancel)} pending TP/SL order(s). Canceling them now...") 
            session.trade.cancel_orders(symbol=symbol, order_list=orders_to_cancel) 
        else: 
            print("No pending TP/SL orders found for this symbol.") 
            
    except Exception as e: 
        print(f"Error while canceling TP/SL orders: {e}") 

def cancel_existing_tp_limit_orders(symbol, position_side):
    """
    Finds and cancels all open LIMIT orders that are opposite to the current position's side.
    This is used to clear previous Take Profit orders before placing a new one.
    """
    try:
        opposite_side = "SELL" if position_side == "BUY" else "BUY"
        
        pending_orders_response = session.trade.get_symbol_open_orders(symbol=symbol)
        
        order_list = pending_orders_response.get('orderList', [])

        if not order_list:
            return

        # Filter for LIMIT orders on the opposite side
        tp_orders_to_cancel = [
            {'orderId': order['orderId']} 
            for order in order_list 
            if order.get('orderType') == 'LIMIT' and order.get('side') == opposite_side
        ]
        
        if tp_orders_to_cancel:
            print(f"Found {len(tp_orders_to_cancel)} open LIMIT order(s) on the {opposite_side} side. Canceling them...")
            session.trade.cancel_orders(symbol=symbol, order_list=tp_orders_to_cancel)
        else:
            print("No opposing TP LIMIT orders found.")
            
    except Exception as e:
        print(f"Error while canceling TP limit orders: {e}")

def set_position_sl(symbol, position_id, sl_price): 
    """
    Places a new stop-loss order linked to a specific position.
    """
    adjusted_sl_price = adjust_price_to_precision(symbol, sl_price) 
    
    # Prepare parameters for the API call 
    api_params = { 
        "symbol": symbol, 
        "position_id": str(position_id), 
        "sl_price": str(adjusted_sl_price) 
    } 
    
    try: 
        response = session.trade.place_position_tpsl_order(**api_params) 
        print(f"Successfully placed SL order!") 
        return response 
    except Exception as e: 
        print(f"Error placing SL order: {e}") 
        return None 


def set_limit_tp_order(symbol, side, position_id, position_qty, tp_price):
    """
    Places a new limit order to act as a take-profit, effectively closing the position.
    """
    # Determine the opposite side for the closing order
    close_side = "SELL" if side == "BUY" else "BUY"
    
    adjusted_tp_price = adjust_price_to_precision(symbol, tp_price)
        
    try:
        response = session.trade.place_order(
            symbol=symbol,
            side=close_side,
            order_type="LIMIT",
            qty=str(position_qty),
            price=str(adjusted_tp_price),
            trade_side="CLOSE",
            position_id=str(position_id)
        )
        print(f"Successfully placed TP LIMIT order!")
        return response
    except Exception as e:
        print(f"Error placing TP LIMIT order: {e}")
        return None 

# ============================================================================== 
# USER INTERACTION 
# ============================================================================== 

def get_user_settings():
    """
    Handles user input to configure the bot's parameters for a trading session.
    It asks for the ticker, stop-loss value, and optionally take-profit percentage.
    
    Returns:
        A tuple containing: (symbol, stop_loss_usd, is_tp_active, tp_percentage)
        Returns (None, 0, False, 0.0) if the user provides invalid input.
    """
    try:
        tick = input(">> Enter the Ticker to operate (e.g., BTC): ").upper()
        if not tick:
            print("Invalid input. Ticker cannot be empty.")
            return None, 0, False, 0.0

        symbol = tick + 'USDT'
        
        sl_input = float(input(f">> Enter the max loss in USDT for {symbol}: "))
        if sl_input <= 0:
            print("Stop-loss value must be a positive number.")
            return None, 0, False, 0.0
        
        stop_loss_usd = sl_input
        is_tp_active = False
        tp_percentage = 0.0

        tp_choice = input(">> Do you want to set an automatic Take Profit? (y/N): ").lower()
        if tp_choice == 'y':
            try:
                tp_input = float(input(">> Enter the TP percentage (e.g., 1 for 1% or 1.5 for 1.5%): "))
                if tp_input > 0:
                    is_tp_active = True
                    tp_percentage = tp_input
                else:
                    print("TP percentage must be positive. TP will not be set.")
            except ValueError:
                print("Invalid percentage. TP will not be set.")
        else:
            print("Take Profit not activated.")
            
        return symbol, stop_loss_usd, is_tp_active, tp_percentage

    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None, 0, False, 0.0

# ==============================================================================
# MAIN CLEANING
# ==============================================================================

def reset_bot_state():
    """
    Resets all global state variables to their default initial values.
    This is used to ensure a clean state after a position is closed or an error occurs.
    """
    global is_active, symbol, stop_loss_usd, tracked_position_value, is_tp_active, tp_percentage
    
    print("Returning to inactive mode.")
    is_active = False
    tracked_position_value = 0
    symbol = ''
    is_tp_active = False
    tp_percentage = 0.0

# ==============================================================================
# MAIN BOT LOOP
# ==============================================================================

def main(): 
    global is_active, symbol, stop_loss_usd, tracked_position_value, is_tp_active, tp_percentage

    while True: 
        try: 
            # ------------------------------------------------------------------
            # ACTIVE STATE LOGIC
            # ------------------------------------------------------------------
            if is_active: 
                # 1. Get the current open position for the symbol. 
                current_position = session.account.get_symbol_open_position(symbol=symbol) 
                
                if current_position and float(current_position.get('qty', 0)) != 0: 
                    # 2. Extract key data from the position. 
                    entry_price = float(current_position['avgOpenPrice']) 
                    position_value_usdt = float(current_position['entryValue']) 
                    side = current_position['side']  # 'BUY' or 'SELL' 
                    position_id = current_position['positionId'] 
                    position_qty = float(current_position['qty'])
                                        
                    # 3. If the position value has changed, update the orders.
                    if position_value_usdt != tracked_position_value:
                        print("Position value has changed! Updating orders...")
                        
                        # 4. Calculate the stop-loss trigger price.
                        percentage = (stop_loss_usd * 100) / position_value_usdt
                        price_variation = entry_price * (percentage / 100)
                        stop_price = entry_price - price_variation if side == 'BUY' else entry_price + price_variation

                        # 5. Validate the calculated stop price.
                        if stop_price <= 0:
                            print("WARNING: Calculated stop-loss price is zero or negative. Order will not be placed.")
                        else:
                            cancel_existing_tpsl_orders(symbol)
                            set_position_sl(symbol, position_id, stop_price)

                        # 6. Calculate Take Profit price if enabled
                        if is_tp_active:
                            # First, cancel any existing opposing limit orders to prevent conflicts.
                            cancel_existing_tp_limit_orders(symbol, side)
                            
                            tp_price_variation = entry_price * (tp_percentage / 100)
                            take_profit_price = entry_price + tp_price_variation if side == 'BUY' else entry_price - tp_price_variation
                            set_limit_tp_order(symbol, side, position_id, position_qty, take_profit_price)
                        
                        tracked_position_value = position_value_usdt
                    
                else: 
                    # 7. If no position is found, it means it has been closed. 
                    print(f"Position for {symbol} has been closed. Cleaning up all open orders for this symbol.") 
                    session.trade.cancel_all_orders(symbol=symbol) # Clean up any orphan orders. 
                    reset_bot_state()

            # ------------------------------------------------------------------
            # INACTIVE STATE LOGIC
            # ------------------------------------------------------------------
            else:
                # Get settings from the user
                new_symbol, new_sl_usd, new_tp_active, new_tp_percentage = get_user_settings()
                
                if new_symbol:
                    # Check if a position is already open for the configured symbol.
                    position = session.account.get_symbol_open_position(symbol=new_symbol)
                    
                    if position and float(position.get('qty', 0)) != 0:
                        print(f"Open position found for {new_symbol}! Starting monitoring...")
                        # Assign the new settings to the global state variables
                        symbol = new_symbol
                        stop_loss_usd = new_sl_usd
                        is_tp_active = new_tp_active
                        tp_percentage = new_tp_percentage
                        is_active = True
                        tracked_position_value = 0 # Reset to force the first SL placement.
                    else:
                        print(f"No open position found for {new_symbol}. Please open a position to start monitoring.")

        # ------------------------------------------------------------------
        # ERROR HANDLING
        # ------------------------------------------------------------------
        except Exception as e: 
            print(f"\nUNEXPECTED ERROR in main loop: {e}") 
            print("Resetting bot to initial state in 10 seconds.") 
            reset_bot_state()
            time.sleep(10) 

        # ------------------------------------------------------------------
        # LOOP PAUSE
        # ------------------------------------------------------------------
        time.sleep(1) # 1-second pause to avoid API rate limits. 

# ============================================================================== 
# SCRIPT ENTRY POINT 
# ============================================================================== 
if __name__ == "__main__": 
    main()