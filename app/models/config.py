from beanie import Document

class MarketStatus(Document):
    is_open: bool = True  # Default to Open

    class Settings:
        name = "market_status"