from AlgorithmImports import *
from custom_vix_data import CustomExternalVIX
import json

class VixFilteredMomentumStrategy(QCAlgorithm):
    """
    Final Project: Regime-Filtered Momentum Strategy
    Thesis: Trend-following fails during high volatility (Regime Change). 
    We use external VIX data to block trades during market panic, while 
    using Reality Modelling and State Persistence to defend against failure modes.
    """
    def initialize(self):
        self.set_start_date(2014, 1, 1) 
        self.set_end_date(2017, 1, 1)
        self.set_cash(100000)
        
        # 1. CORE ASSET (Standard QC Data)
        self.aapl = self.add_equity("AAPL", Resolution.DAILY)
        self.aapl_symbol = self.aapl.symbol
        
        # 2. EXTERNAL DATA (The VIX Fear Gauge)
        self.vix = self.add_data(CustomExternalVIX, "EXT_VIX", Resolution.DAILY)
        self.vix_symbol = self.vix.symbol
        
        # 3. REALITY MODELLING (Defending against Analytical Failures)
        self.aapl.set_fee_model(ConstantFeeModel(1.00)) 
        self.aapl.set_slippage_model(ConstantSlippageModel(0.01)) 
        
        self.fast_ema = self.ema(self.aapl_symbol, 15, Resolution.DAILY)
        self.slow_ema = self.ema(self.aapl_symbol, 50, Resolution.DAILY)
        self.set_warm_up(50)
        
        # 4. STATE PERSISTENCE (Defending against Mechanical Failures)
        self.state_key = "vix_algo_state"
        if self.object_store.contains_key(self.state_key):
            saved_state = json.loads(self.object_store.read(self.state_key))
            self.is_long = saved_state.get("is_long", False)
        else:
            self.is_long = False
            
    def save_algo_state(self):
        self.object_store.save(self.state_key, json.dumps({"is_long": self.is_long}))
        
    def on_data(self, data):
        if self.is_warming_up or not data.contains_key(self.aapl_symbol):
            return
        if not (self.fast_ema.is_ready and self.slow_ema.is_ready):
            return
            
        # REGIME CHECK: Get the current fear level, default to 20 (calm) if data is missing
        current_vix = 20 
        if data.contains_key(self.vix_symbol):
            current_vix = data[self.vix_symbol].value
            
        fast_val = self.fast_ema.current.value
        slow_val = self.slow_ema.current.value
        
        # BUY LOGIC: Only buy if the trend is up AND the market is calm (VIX < 25)
        if fast_val > slow_val and not self.is_long and current_vix < 25:
            self.set_holdings(self.aapl_symbol, 1.0)
            self.is_long = True
            self.save_algo_state() 
            self.debug(f"BUY AAPL | VIX is safe at {current_vix}")
            
        # SELL LOGIC: Sell if the trend breaks OR if the market suddenly panics (VIX > 30)
        elif self.is_long and (fast_val < slow_val or current_vix > 30):
            self.liquidate(self.aapl_symbol)
            self.is_long = False
            self.save_algo_state() 
            self.debug(f"SELL AAPL | Trend broke or VIX spiked to {current_vix}")

    def on_end_of_algorithm(self):
        self.log(f"Final Value: ${self.portfolio.total_portfolio_value:,.2f}")
