"""Seed dữ liệu mặc định: admin user, danh mục mặc định."""

import logging
import bcrypt
from datetime import datetime, timezone
from db.database import get_session
from models.user import User
from models.category import Category, SubCategory
from config import settings

logger = logging.getLogger(__name__)

DEFAULT_CATEGORIES = [
    {
        "name": "Thu nhập",
        "type": "income",
        "icon": "💰",
        "color": "#4CAF50",
        "subs": ["Lương", "Thưởng", "Freelance", "Hoàn tiền", "Lãi tiết kiệm", "Quà tặng", "Thu nhập khác"],
    },
    {
        "name": "Chi cố định",
        "type": "expense_fixed",
        "icon": "🏠",
        "color": "#F44336",
        "subs": ["Thuê nhà", "Điện", "Nước", "Internet/Điện thoại", "Học phí", "Bảo hiểm", "Trả nợ/vay", "Phí dịch vụ"],
    },
    {
        "name": "Chi biến đổi",
        "type": "expense_variable",
        "icon": "🛒",
        "color": "#FF9800",
        "subs": [
            "Ăn uống", "Đi lại", "Sức khỏe", "Mua sắm",
            "Giải trí", "Hiếu hỉ", "Du lịch", "Chăm sóc cá nhân",
            "Giáo dục", "Từ thiện", "Chi khác",
        ],
    },
    {
        "name": "Tiết kiệm / Đầu tư",
        "type": "saving",
        "icon": "📈",
        "color": "#2196F3",
        "subs": ["Gửi tiết kiệm", "Đầu tư", "Mua vàng", "Mua ngoại tệ"],
    },
    {
        "name": "Chuyển khoản nội bộ",
        "type": "transfer",
        "icon": "🔄",
        "color": "#9E9E9E",
        "subs": ["Chuyển khoản"],
    },
]


def seed_admin_user() -> bool:
    """Đảm bảo user quản trị mặc định luôn đúng theo cấu hình."""
    session = get_session()
    try:
        target = session.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        changed = False

        if target:
            setattr(target, "display_name", settings.ADMIN_DISPLAY_NAME)
            setattr(target, "is_active", 1)
            if not bcrypt.checkpw(
                settings.ADMIN_PASSWORD.encode("utf-8"),
                target.password_hash.encode("utf-8"),
            ):
                hashed = bcrypt.hashpw(settings.ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt())
                target.password_hash = hashed.decode("utf-8")
            changed = True
            logger.info("Đã cập nhật user quản trị: %s", settings.ADMIN_USERNAME)
        else:
            hashed = bcrypt.hashpw(settings.ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt())
            admin = User(
                username=settings.ADMIN_USERNAME,
                password_hash=hashed.decode("utf-8"),
                display_name=settings.ADMIN_DISPLAY_NAME,
                is_active=1,
            )
            session.add(admin)
            changed = True
            logger.info("Đã tạo user quản trị: %s", settings.ADMIN_USERNAME)

        # Vô hiệu hoá tài khoản admin mặc định cũ nếu đổi username quản trị
        if settings.ADMIN_USERNAME != "admin":
            legacy_admin = session.query(User).filter(User.username == "admin").first()
            if legacy_admin is not None and int(getattr(legacy_admin, "is_active", 0)) == 1:
                setattr(legacy_admin, "is_active", 0)
                changed = True
                logger.info("Đã vô hiệu hóa user quản trị cũ: admin")

        session.commit()
        return changed
    except Exception as e:
        session.rollback()
        logger.error(f"Lỗi seed admin: {e}")
        raise
    finally:
        session.close()


def seed_default_categories() -> int:
    """Tạo danh mục mặc định nếu chưa có (system categories, user_id=NULL)."""
    session = get_session()
    try:
        existing = session.query(Category).filter(Category.is_system == 1).count()
        if existing > 0:
            logger.info("Danh mục mặc định đã tồn tại, bỏ qua seed.")
            return 0

        count = 0
        for idx, cat_data in enumerate(DEFAULT_CATEGORIES):
            cat = Category(
                user_id=None,
                name=cat_data["name"],
                type=cat_data["type"],
                icon=cat_data["icon"],
                color=cat_data["color"],
                sort_order=idx,
                is_system=1,
                is_active=1,
            )
            session.add(cat)
            session.flush()

            for sub_idx, sub_name in enumerate(cat_data["subs"]):
                sub = SubCategory(
                    category_id=cat.id,
                    name=sub_name,
                    sort_order=sub_idx,
                    is_active=1,
                )
                session.add(sub)
                count += 1

        session.commit()
        logger.info(f"Đã tạo {len(DEFAULT_CATEGORIES)} danh mục và {count} danh mục con.")
        return count
    except Exception as e:
        session.rollback()
        logger.error(f"Lỗi seed categories: {e}")
        raise
    finally:
        session.close()


def run_all_seeds() -> None:
    """Chạy tất cả seed."""
    seed_admin_user()
    seed_default_categories()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from db.init_db import init_database
    init_database()
    run_all_seeds()
    print("Seed dữ liệu hoàn tất!")
