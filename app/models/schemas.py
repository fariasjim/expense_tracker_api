from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field


class Category(str, Enum):
    # Core Living Expenses
    HOUSING = "Housing"  # Rent, mortgage, property tax
    UTILITIES = "Utilities"  # Electricity, water, gas, internet, phone
    GROCERIES = "Groceries"  # Supermarket runs, food shopping

    # Daily Life & Commute
    TRANSPORTATION = "Transportation"  # Fuel, public transit, Uber, car maintenance
    FOOD_DINING = "Food & Dining"  # Restaurants, coffee shops, takeout

    # Lifestyle & Personal Care
    ENTERTAINMENT = "Entertainment"  # Movies, concerts, streaming services, hobbies
    SHOPPING = "Shopping"  # Clothes, electronics, home decor
    HEALTH_FITNESS = "Health & Fitness"  # Meds, doctor visits, gym, health insurance

    # Financial Commitments
    INSURANCE = "Insurance"  # Auto, life, or home insurance (if separate)
    DEBT_LOANS = "Debt & Loans"  # Credit card payments, student loans, personal loans
    SAVINGS_INVESTING = "Savings & Investing"  # Emergency fund, stocks, crypto

    # Miscellanous / Administrative
    EDUCATION = "Education"  # Tuition, books, courses
    GIFTS_DONATIONS = "Gifts & Donations"  # Charity, birthday presents
    MISCELLANEOUS = "Miscellaneous"  # One-off expenses, unexpected costs


class ExpenseType(str, Enum):
    # Enum model for ExpenseType category
    DEBIT = "Debit"
    CREDIT = "Credit"


class Signup(BaseModel):
    name: str
    password: str


class GlobalResponseModel(BaseModel):
    status: HTTPStatus
    message: str


class User(SQLModel, table=True):
    """
    User table with expenses relational table which connects with Expenses table by id.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default=None, index=True)
    email: str = Field(default=None, unique=True)
    password: str = Field(default=None)
    expenses: List["Expenses"] = Relationship(back_populates="user")


class Expenses(SQLModel, table=True):
    """
    Expenses table which connects with User table with relation of user.id at user.expenses[List].
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default=None, index=True)
    category: Category = Field(default=Category.MISCELLANEOUS)
    type: ExpenseType = Field(default=ExpenseType.DEBIT)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    date: datetime = Field(default=lambda: datetime.now(timezone.utc))
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="expenses")
