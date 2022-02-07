import alpaca_trade_api as tradeapi


APCA_API_BASE_URL= "https://paper-api.alpaca.markets"
APCA_API_KEY_ID= "PKVJGXTP6DYLE10H4DEX"
APCA_API_SECRET_KEY= "4ERoxoZme51VzOtCaMh4rb5OGhn3m3euXHNhU2Nm"


"""
APCA_API_BASE_URL= "https://api.alpaca.markets"
APCA_API_KEY_ID= "AKUO8BA5HJXT2Q70GRHB"
APCA_API_SECRET_KEY= "DzYTpvxuLZmjD4socdsNdpfA2yl2NotP243E0s7M"
"""

api = tradeapi.REST(
    base_url=APCA_API_BASE_URL,
    key_id=APCA_API_KEY_ID,
    secret_key=APCA_API_SECRET_KEY
)
