# config.py
from decimal import Decimal
import logging

DB_PATH = "trading_system.db"
DEFAULT_SAFETY_BUFFER = Decimal("0.25")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("System")
