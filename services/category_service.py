"""Category service - Quản lý danh mục."""

import logging
from typing import List, Optional
from db.database import get_session
from models.category import Category, SubCategory
from repositories.category_repo import CategoryRepository, SubCategoryRepository

logger = logging.getLogger(__name__)


class CategoryService:
    """Dịch vụ danh mục thu chi."""

    @staticmethod
    def get_categories(user_id: int) -> List[Category]:
        session = get_session()
        try:
            return CategoryRepository(session).get_for_user(user_id)
        finally:
            session.close()

    @staticmethod
    def get_income_categories(user_id: int) -> List[Category]:
        session = get_session()
        try:
            return CategoryRepository(session).get_income_categories(user_id)
        finally:
            session.close()

    @staticmethod
    def get_expense_categories(user_id: int) -> List[Category]:
        session = get_session()
        try:
            return CategoryRepository(session).get_expense_categories(user_id)
        finally:
            session.close()

    @staticmethod
    def get_subcategories(category_id: int) -> List[SubCategory]:
        session = get_session()
        try:
            return SubCategoryRepository(session).get_by_category(category_id)
        finally:
            session.close()

    @staticmethod
    def create_category(user_id: int, name: str, cat_type: str, icon: str = "", color: str = "") -> tuple:
        session = get_session()
        try:
            repo = CategoryRepository(session)
            cat = Category(
                user_id=user_id,
                name=name,
                type=cat_type,
                icon=icon,
                color=color,
                is_system=0,
                is_active=1,
            )
            repo.create(cat)
            session.commit()
            return True, "Tạo danh mục thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def create_subcategory(category_id: int, name: str) -> tuple:
        session = get_session()
        try:
            sub = SubCategory(category_id=category_id, name=name, is_active=1)
            session.add(sub)
            session.commit()
            return True, "Tạo danh mục con thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_category_map(user_id: int) -> dict:
        """Trả về dict {category_id: category_name}."""
        cats = CategoryService.get_categories(user_id)
        return {c.id: f"{c.icon} {c.name}" if c.icon else c.name for c in cats}

    @staticmethod
    def delete_category(category_id: int) -> tuple:
        """Xóa nhóm danh mục (và tất cả danh mục con)."""
        session = get_session()
        try:
            repo = CategoryRepository(session)
            cat = repo.get_by_id(category_id)
            if not cat:
                return False, "Không tìm thấy danh mục"
            if cat.is_system:
                return False, "Không thể xóa danh mục hệ thống"
            # Xóa danh mục con trước
            subs = SubCategoryRepository(session).get_by_category(category_id)
            for sub in subs:
                session.delete(sub)
            session.delete(cat)
            session.commit()
            return True, "Đã xóa nhóm danh mục"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def delete_subcategory(subcategory_id: int) -> tuple:
        """Xóa danh mục con."""
        session = get_session()
        try:
            sub = session.query(SubCategory).get(subcategory_id)
            if not sub:
                return False, "Không tìm thấy danh mục con"
            session.delete(sub)
            session.commit()
            return True, "Đã xóa danh mục con"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_subcategory_map(user_id: int) -> dict:
        """Trả về dict {subcategory_id: subcategory_name}."""
        session = get_session()
        try:
            cats = CategoryRepository(session).get_for_user(user_id)
            result = {}
            sub_repo = SubCategoryRepository(session)
            for cat in cats:
                subs = sub_repo.get_by_category(cat.id)
                for s in subs:
                    result[s.id] = s.name
            return result
        finally:
            session.close()
