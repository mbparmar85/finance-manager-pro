from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def money(value):
    """Convert value to Decimal with 2 decimal places."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    accounts = db.relationship("Account", backref="user", lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship("Expense", backref="user", lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="user", lazy=True, cascade="all, delete-orphan")
    loans = db.relationship("Loan", backref="user", lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Return user ID for Flask-Login."""
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default="USD")
    balance = db.Column(db.String(30), nullable=False, default="0.00")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "name", name="uq_account_user_name"),)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "currency": self.currency,
            "balance": float(self.balance or "0.00"),
        }


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(255), default="")
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    account = db.relationship("Account")

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "amount": float(self.amount or "0.00"),
            "description": self.description,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else "",
            "currency": self.account.currency if self.account else "USD",
        }


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.String(30), nullable=False)
    month = db.Column(db.String(10), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "category", "month", name="uq_budget_user_category_month"),)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "amount": float(self.amount or "0.00"),
            "month": self.month,
        }


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    principal = db.Column(db.String(30), nullable=False)
    remaining_amount = db.Column(db.String(30), nullable=False)
    interest_rate = db.Column(db.String(20), nullable=False, default="0")
    currency = db.Column(db.String(10), nullable=False, default="USD")
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    account = db.relationship("Account")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "principal": float(self.principal or "0.00"),
            "remaining_amount": float(self.remaining_amount or "0.00"),
            "interest_rate": float(self.interest_rate or "0.00"),
            "currency": self.currency,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }


class LoanPayment(db.Model):
    __tablename__ = "loan_payments"

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey("loans.id"), nullable=False, index=True)
    amount = db.Column(db.String(30), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "loan_id": self.loan_id,
            "amount": float(self.amount or "0.00"),
            "payment_date": self.payment_date.strftime("%Y-%m-%d"),
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    loan_id = db.Column(db.Integer, db.ForeignKey("loans.id"), nullable=True)
    amount = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(255), default="")
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    account = db.relationship("Account")
    loan = db.relationship("Loan")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "amount": float(self.amount or "0.00"),
            "description": self.description,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "account_name": self.account.name if self.account else None,
            "currency": self.account.currency if self.account else None,
            "loan_name": self.loan.name if self.loan else None,
        }
