"""
Economic Data Monitoring Configuration
"""

# Economic indicators to monitor
ECONOMIC_INDICATORS = {
    'stock_indices': {
        'KOSPI': {
            'symbol': '^KS11',
            'name': 'KOSPI',
            'threshold_surge': 2.0,  # 2% or more rise
            'threshold_drop': -2.0,  # 2% or more drop
            'volatility_threshold': 3.0  # 3% or more volatility
        },
        'KOSDAQ': {
            'symbol': '^KQ11',
            'name': 'KOSDAQ',
            'threshold_surge': 3.0,
            'threshold_drop': -3.0,
            'volatility_threshold': 4.0
        },
        'S&P500': {
            'symbol': '^GSPC',
            'name': 'S&P 500',
            'threshold_surge': 1.5,
            'threshold_drop': -1.5,
            'volatility_threshold': 2.5
        },
        'NASDAQ': {
            'symbol': '^IXIC',
            'name': 'NASDAQ',
            'threshold_surge': 2.0,
            'threshold_drop': -2.0,
            'volatility_threshold': 3.0
        }
    },
    'currencies': {
        'USD_KRW': {
            'symbol': 'USDKRW=X',
            'name': 'USD/KRW',
            'threshold_surge': 1.0,
            'threshold_drop': -1.0,
            'volatility_threshold': 1.5
        },
        'EUR_KRW': {
            'symbol': 'EURKRW=X',
            'name': 'EUR/KRW',
            'threshold_surge': 1.0,
            'threshold_drop': -1.0,
            'volatility_threshold': 1.5
        }
    },
    'forex_pairs': {
        'EUR_USD': {
            'symbol': 'EURUSD=X',
            'name': 'EUR/USD',
            'threshold_surge': 0.5,    # 0.5% = ~50 pips
            'threshold_drop': -0.5,
            'volatility_threshold': 1.0,
            'pip_value': 0.0001,
            'pip_threshold': 50         # 50 pips = significant move
        },
        'GBP_USD': {
            'symbol': 'GBPUSD=X',
            'name': 'GBP/USD',
            'threshold_surge': 0.5,
            'threshold_drop': -0.5,
            'volatility_threshold': 1.0,
            'pip_value': 0.0001,
            'pip_threshold': 50
        },
        'USD_JPY': {
            'symbol': 'USDJPY=X',
            'name': 'USD/JPY',
            'threshold_surge': 0.4,    # 0.4% = ~50 pips
            'threshold_drop': -0.4,
            'volatility_threshold': 0.8,
            'pip_value': 0.01,
            'pip_threshold': 50
        },
        'AUD_USD': {
            'symbol': 'AUDUSD=X',
            'name': 'AUD/USD',
            'threshold_surge': 0.6,
            'threshold_drop': -0.6,
            'volatility_threshold': 1.2,
            'pip_value': 0.0001,
            'pip_threshold': 50
        },
        'USD_CAD': {
            'symbol': 'USDCAD=X',
            'name': 'USD/CAD',
            'threshold_surge': 0.5,
            'threshold_drop': -0.5,
            'volatility_threshold': 1.0,
            'pip_value': 0.0001,
            'pip_threshold': 50
        },
        'NZD_USD': {
            'symbol': 'NZDUSD=X',
            'name': 'NZD/USD',
            'threshold_surge': 0.6,
            'threshold_drop': -0.6,
            'volatility_threshold': 1.2,
            'pip_value': 0.0001,
            'pip_threshold': 50
        },
        'USD_CHF': {
            'symbol': 'USDCHF=X',
            'name': 'USD/CHF',
            'threshold_surge': 0.5,
            'threshold_drop': -0.5,
            'volatility_threshold': 1.0,
            'pip_value': 0.0001,
            'pip_threshold': 50
        },
        'EUR_JPY': {
            'symbol': 'EURJPY=X',
            'name': 'EUR/JPY',
            'threshold_surge': 0.5,
            'threshold_drop': -0.5,
            'volatility_threshold': 1.0,
            'pip_value': 0.01,
            'pip_threshold': 60
        },
        'GBP_JPY': {
            'symbol': 'GBPJPY=X',
            'name': 'GBP/JPY',
            'threshold_surge': 0.5,
            'threshold_drop': -0.5,
            'volatility_threshold': 1.0,
            'pip_value': 0.01,
            'pip_threshold': 70
        },
        'EUR_GBP': {
            'symbol': 'EURGBP=X',
            'name': 'EUR/GBP',
            'threshold_surge': 0.4,
            'threshold_drop': -0.4,
            'volatility_threshold': 0.8,
            'pip_value': 0.0001,
            'pip_threshold': 40
        }
    },
    'commodities': {
        'CRUDE_OIL': {
            'symbol': 'CL=F',
            'name': 'Crude Oil',
            'threshold_surge': 3.0,
            'threshold_drop': -3.0,
            'volatility_threshold': 4.0
        },
        'GOLD': {
            'symbol': 'GC=F',
            'name': 'Gold',
            'threshold_surge': 2.0,
            'threshold_drop': -2.0,
            'volatility_threshold': 2.5
        }
    }
}

# Monitoring settings
MONITORING_CONFIG = {
    'check_interval': 60,  # Check every 60 seconds
    'data_retention_days': 30,  # Retain data for 30 days
    'alert_cooldown': 300,  # Prevent same alert for 5 minutes
    'batch_size': 10,  # Number of indicators to process at once
}

# Event severity calculation weights
SEVERITY_WEIGHTS = {
    'price_change_magnitude': 0.4,  # Price change magnitude
    'volume_spike': 0.3,  # Volume spike
    'market_correlation': 0.2,  # Market correlation
    'historical_significance': 0.1  # Historical significance
}

# Data source settings
DATA_SOURCES = {
    'yahoo_finance': {
        'enabled': True,
        'api_key': None,  # Yahoo Finance is free
        'rate_limit': 2000  # Requests per hour
    },
    'alpha_vantage': {
        'enabled': False,
        'api_key': 'YOUR_API_KEY',
        'rate_limit': 500
    },
    'fred': {  # Federal Reserve Economic Data
        'enabled': False,
        'api_key': 'YOUR_FRED_API_KEY',
        'rate_limit': 120
    }
}
