"""Auth service - Xác thực và quản lý phiên."""

import logging
import bcrypt
from typing import Optional, Tuple

from db.database import get_session
from config import settings
from models.user import User
from repositories.user_repo import UserRepository
from repositories.audit_repo import AuditRepository
from db.seed import seed_admin_user

logger = logging.getLogger(__name__)


class AuthService:
    """Dịch vụ xác thực."""

    @staticmethod
    def login(username: str, password: str) -> Tuple[bool, Optional[dict], str]:
        """Đăng nhập. Trả về (success, user_data, message)."""
        username = (username or "").strip()
        session = get_session()
        try:
            repo = UserRepository(session)
            user = repo.get_by_username(username)

            if not user:
                # Tự phục hồi admin mặc định nếu DB hiện tại chưa có user này
                if username == settings.ADMIN_USERNAME:
                    session.close()
                    seed_admin_user()
                    session = get_session()
                    repo = UserRepository(session)
                    user = repo.get_by_username(username)

            if not user:
                return False, None, "Tên đăng nhập không tồn tại"

            if not user.is_active:
                return False, None, "Tài khoản đã bị khóa"

            if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
                return False, None, "Mật khẩu không đúng"

            # Log audit
            audit = AuditRepository(session)
            audit.log_action(user.id, "login")
            session.commit()

            user_data = {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "email": user.email,
            }
            return True, user_data, "Đăng nhập thành công"

        except Exception as e:
            logger.error(f"Lỗi đăng nhập: {e}")
            return False, None, "Lỗi hệ thống"
        finally:
            session.close()

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Đổi mật khẩu."""
        session = get_session()
        try:
            repo = UserRepository(session)
            user = repo.get_by_id(user_id)

            if not user:
                return False, "Không tìm thấy người dùng"

            if not bcrypt.checkpw(old_password.encode("utf-8"), user.password_hash.encode("utf-8")):
                return False, "Mật khẩu cũ không đúng"

            new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            user.password_hash = new_hash.decode("utf-8")

            audit = AuditRepository(session)
            audit.log_action(user_id, "change_password")
            session.commit()

            return True, "Đổi mật khẩu thành công"

        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi đổi mật khẩu: {e}")
            return False, "Lỗi hệ thống"
        finally:
            session.close()

    @staticmethod
    def create_user(username: str, password: str, display_name: str, email: str = None) -> Tuple[bool, str]:
        """Tạo user mới."""
        username = (username or "").strip()
        display_name = (display_name or "").strip()
        session = get_session()
        try:
            repo = UserRepository(session)
            if repo.username_exists(username):
                return False, "Tên đăng nhập đã tồn tại"

            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            user = User(
                username=username,
                password_hash=hashed.decode("utf-8"),
                display_name=display_name,
                email=email,
                is_active=1,
            )
            repo.create(user)
            session.commit()
            return True, "Tạo người dùng thành công"

        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi tạo user: {e}")
            return False, "Lỗi hệ thống"
        finally:
            session.close()

    @staticmethod
    def has_any_user() -> bool:
        """Kiểm tra đã có user nào chưa."""
        session = get_session()
        try:
            return session.query(User).count() > 0
        finally:
            session.close()
