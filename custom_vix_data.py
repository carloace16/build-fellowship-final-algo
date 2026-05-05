from AlgorithmImports import *
from datetime import datetime, timedelta

class CustomExternalVIX(PythonData):
    """
    Defines the external data source for the CBOE Volatility Index (VIX).
    """
    def get_source(self, config: SubscriptionDataConfig, date: datetime, is_live_mode: bool) -> SubscriptionDataSource:
        # Use CBOE's historical VIX data from QuantConnect's data library
        # Format: YYYYMMDD
        url = f"https://www.dropbox.com/s/3qz9r5q5a8c9h3v/vix-daily.csv?dl=1"
        return SubscriptionDataSource(url, SubscriptionTransportMedium.REMOTE_FILE)
    
    def reader(self, config: SubscriptionDataConfig, line: str, date: datetime, is_live_mode: bool) -> BaseData:
        # Skip header rows, empty lines, and error messages (like "404: Not Found")
        if not line or not line.strip():
            return None
        
        # Check if line starts with a digit (valid date)
        if not line[0].isdigit():
            return None
        
        # Ignore HTTP error messages
        if "404" in line or "Not Found" in line or "Error" in line:
            return None
            
        index = CustomExternalVIX()
        index.symbol = config.symbol
        
        try:
            csv_row = line.split(',')
            
            # Ensure we have enough columns
            if len(csv_row) < 5:
                return None
                
            date_string = str(csv_row[0]).strip()
            
            index.time = datetime.strptime(date_string, "%Y-%m-%d")
            index.end_time = index.time + timedelta(days=1)
            
            # The VIX Close value is the 5th column
            index.value = float(csv_row[4].strip())
            
        except Exception:
            return None
            
        return index
