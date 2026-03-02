"""Category & SubCategory models - Danh mục thu chi."""

from sqlalchemy import Column, Integer, String, ForeignKey
from models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # NULL = system default
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # income, expense_fixed, expense_variable, saving, transfer
    icon = Column(String(10), nullable=True)
    color = Column(String(20), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_system = Column(Integer, default=0, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"


class SubCategory(Base, TimestampMixin):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<SubCategory(id={self.id}, name='{self.name}')>"
