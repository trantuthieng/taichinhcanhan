"""Khởi tạo database - tạo tất cả bảng."""

import logging
from models import Base
from db.database import engine

logger = logging.getLogger(__name__)


def init_database() -> None:
    """Tạo tất cả bảng trong database nếu chưa tồn tại."""
    logger.info("Khởi tạo database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database đã sẵn sàng.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
    print("Database khởi tạo thành công!")
