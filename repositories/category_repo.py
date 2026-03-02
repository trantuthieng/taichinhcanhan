"""Category repository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from models.category import Category, SubCategory
from repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: Session):
        super().__init__(Category, session)

    def get_for_user(self, user_id: int) -> List[Category]:
        """System categories + user's custom categories."""
        return (
            self.session.query(Category)
            .filter(
                ((Category.user_id == None) | (Category.user_id == user_id)),
                Category.is_active == 1,
            )
            .order_by(Category.sort_order, Category.name)
            .all()
        )

    def get_by_type(self, user_id: int, cat_type: str) -> List[Category]:
        return (
            self.session.query(Category)
            .filter(
                ((Category.user_id == None) | (Category.user_id == user_id)),
                Category.type == cat_type,
                Category.is_active == 1,
            )
            .order_by(Category.sort_order)
            .all()
        )

    def get_income_categories(self, user_id: int) -> List[Category]:
        return self.get_by_type(user_id, "income")

    def get_expense_categories(self, user_id: int) -> List[Category]:
        cats = self.get_by_type(user_id, "expense_fixed")
        cats += self.get_by_type(user_id, "expense_variable")
        return cats


class SubCategoryRepository(BaseRepository[SubCategory]):
    def __init__(self, session: Session):
        super().__init__(SubCategory, session)

    def get_by_category(self, category_id: int) -> List[SubCategory]:
        return (
            self.session.query(SubCategory)
            .filter(SubCategory.category_id == category_id, SubCategory.is_active == 1)
            .order_by(SubCategory.sort_order)
            .all()
        )
