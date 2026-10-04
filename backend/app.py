import os
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config import config
from models import Account, Budget, Expense, Loan, LoanPayment, Transaction, User, db, money

login_manager = LoginManager()

EXCHANGE_RATES = {
    "USD": Decimal("1.00"),
    "EUR": Decimal("0.92"),
}


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def convert_amount(amount, from_currency, to_currency):
    amount = money(amount)
    frm = EXCHANGE_RATES[from_currency]
    to = EXCHANGE_RATES[to_currency]
    return money((amount * to) / frm)


def create_app(config_obj=None):
    app = Flask(__name__)
    
    if config_obj is None:
        config_obj = config
    
    app.config.from_object(config_obj)
    app.config["JSON_SORT_KEYS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    
    cors_origins = app.config.get("CORS_ORIGINS", ["http://localhost:5173"])
    if isinstance(cors_origins, str):
        cors_origins = [origin.strip() for origin in cors_origins.split(",")]
    
    CORS(app, supports_credentials=True, origins=cors_origins)

    with app.app_context():
        db.create_all()

    # ============ HEALTH CHECK ============
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})

    # ============ AUTH ROUTES ============
    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not username or not email or not password:
            return jsonify({"error": "Username, email and password are required."}), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"error": "Username or email already exists."}), 409

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Registration successful."}), 201

    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid username or password."}), 401

        login_user(user)
        return jsonify({"user": user.to_dict()})

    @app.route("/api/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return jsonify({"message": "Logged out."})

    @app.route("/api/me", methods=["GET"])
    @login_required
    def get_me():
        return jsonify({"user": current_user.to_dict()})

    # ============ ACCOUNT ROUTES ============
    @app.route("/api/accounts", methods=["GET", "POST"])
    @login_required
    def accounts():
        if request.method == "GET":
            accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name.asc()).all()
            return jsonify({"accounts": [a.to_dict() for a in accounts]})

        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        currency = (data.get("currency") or "USD").upper()

        if not name:
            return jsonify({"error": "Account name is required."}), 400

        if currency not in EXCHANGE_RATES:
            return jsonify({"error": "Unsupported currency."}), 400

        existing = Account.query.filter_by(user_id=current_user.id, name=name).first()
        if existing:
            return jsonify({"error": "Account already exists."}), 409

        account = Account(user_id=current_user.id, name=name, currency=currency, balance="0.00")
        db.session.add(account)
        db.session.commit()
        return jsonify({"account": account.to_dict()}), 201

    @app.route("/api/accounts/<int:account_id>", methods=["POST"])
    @login_required
    def modify_account(account_id):
        data = request.get_json(silent=True) or {}
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            return jsonify({"error": "Account not found."}), 404

        if "name" in data:
            name = (data["name"] or "").strip()
            if not name:
                return jsonify({"error": "Name cannot be empty."}), 400
            account.name = name

        if "currency" in data:
            currency = (data["currency"] or "USD").upper()
            if currency not in EXCHANGE_RATES:
                return jsonify({"error": "Unsupported currency."}), 400
            account.currency = currency

        db.session.commit()
        return jsonify({"account": account.to_dict()})

    # ============ TRANSACTION ROUTES ============
    @app.route("/api/transactions", methods=["GET"])
    @login_required
    def transactions():
        rows = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(200).all()
        return jsonify({"transactions": [t.to_dict() for t in rows]})

    @app.route("/api/deposit", methods=["POST"])
    @login_required
    def deposit():
        data = request.get_json(silent=True) or {}
        account = Account.query.filter_by(id=data.get("account_id"), user_id=current_user.id).first()
        if not account:
            return jsonify({"error": "Account not found."}), 404

        amount = money(data.get("amount", 0))
        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400

        account.balance = str(Decimal(account.balance or "0.00") + amount)
        db.session.add(Transaction(
            user_id=current_user.id,
            type="deposit",
            account_id=account.id,
            amount=str(amount),
            description="Deposit",
            date=datetime.utcnow(),
        ))
        db.session.commit()
        return jsonify({"account": account.to_dict()})

    @app.route("/api/withdraw", methods=["POST"])
    @login_required
    def withdraw():
        data = request.get_json(silent=True) or {}
        account = Account.query.filter_by(id=data.get("account_id"), user_id=current_user.id).first()
        if not account:
            return jsonify({"error": "Account not found."}), 404

        amount = money(data.get("amount", 0))
        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400

        current_balance = Decimal(account.balance or "0.00")
        if amount > current_balance:
            return jsonify({"error": "Insufficient funds."}), 400

        account.balance = str(current_balance - amount)
        db.session.add(Transaction(
            user_id=current_user.id,
            type="withdrawal",
            account_id=account.id,
            amount=str(amount),
            description="Withdrawal",
            date=datetime.utcnow(),
        ))
        db.session.commit()
        return jsonify({"account": account.to_dict()})

    @app.route("/api/transfer", methods=["POST"])
    @login_required
    def transfer():
        data = request.get_json(silent=True) or {}
        from_id = data.get("from_account_id")
        to_id = data.get("to_account_id")
        amount = money(data.get("amount", 0))

        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400

        if from_id == to_id:
            return jsonify({"error": "Source and destination must be different."}), 400

        source = Account.query.filter_by(id=from_id, user_id=current_user.id).first()
        target = Account.query.filter_by(id=to_id, user_id=current_user.id).first()
        if not source or not target:
            return jsonify({"error": "One or both accounts were not found."}), 404

        source_balance = Decimal(source.balance or "0.00")
        if source_balance < amount:
            return jsonify({"error": "Insufficient funds in source account."}), 400

        if source.currency == target.currency:
            converted = amount
        else:
            converted = convert_amount(amount, source.currency, target.currency)

        source.balance = str(source_balance - amount)
        target.balance = str(Decimal(target.balance or "0.00") + converted)

        db.session.add(Transaction(
            user_id=current_user.id,
            type="transfer",
            account_id=source.id,
            amount=str(amount),
            description=f"Transfer to {target.name}",
            date=datetime.utcnow(),
        ))
        db.session.commit()
        return jsonify({"source": source.to_dict(), "target": target.to_dict()})

    # ============ EXPENSE ROUTES ============
    @app.route("/api/expenses", methods=["GET", "POST"])
    @login_required
    def expenses():
        if request.method == "GET":
            category = request.args.get("category")
            query = Expense.query.filter_by(user_id=current_user.id)
            if category:
                query = query.filter_by(category=category)
            rows = query.order_by(Expense.date.desc()).all()
            return jsonify({"expenses": [e.to_dict() for e in rows]})

        data = request.get_json(silent=True) or {}
        account_id = data.get("account_id")
        category = (data.get("category") or "").strip()
        amount = money(data.get("amount", 0))
        description = (data.get("description") or "").strip()

        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400

        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            return jsonify({"error": "Account not found."}), 404

        valid_categories = ["Food", "Transport", "Entertainment", "Utilities", "Healthcare", "Shopping", "Insurance", "Education", "Other"]
        if category not in valid_categories:
            return jsonify({"error": "Invalid category."}), 400

        if amount > Decimal(account.balance or "0.00"):
            return jsonify({"error": "Insufficient funds."}), 400

        account.balance = str(Decimal(account.balance or "0.00") - amount)
        expense = Expense(
            user_id=current_user.id,
            account_id=account.id,
            category=category,
            amount=str(amount),
            description=description,
            date=datetime.utcnow(),
        )
        db.session.add(expense)
        db.session.add(Transaction(
            user_id=current_user.id,
            type="expense",
            account_id=account.id,
            amount=str(amount),
            description=f"{category}: {description or 'Expense'}",
            date=datetime.utcnow(),
        ))
        db.session.commit()
        return jsonify({"expense": expense.to_dict()}), 201

    # ============ BUDGET ROUTES ============
    @app.route("/api/budgets", methods=["GET", "POST"])
    @login_required
    def budgets():
        if request.method == "GET":
            year = request.args.get("year")
            month = request.args.get("month")
            if not year or not month:
                now = datetime.utcnow()
                year = str(now.year)
                month = str(now.month).zfill(2)
            month_key = f"{year}-{str(month).zfill(2)}"
            rows = Budget.query.filter_by(user_id=current_user.id, month=month_key).all()
            return jsonify({"budgets": [b.to_dict() for b in rows]})

        data = request.get_json(silent=True) or {}
        category = (data.get("category") or "").strip()
        amount = money(data.get("amount", 0))
        year = data.get("year")
        month = data.get("month")

        if not category or not year or not month:
            return jsonify({"error": "Category, year and month are required."}), 400

        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400

        month_key = f"{year}-{str(month).zfill(2)}"
        budget = Budget.query.filter_by(user_id=current_user.id, category=category, month=month_key).first()
        if budget:
            budget.amount = str(amount)
        else:
            budget = Budget(user_id=current_user.id, category=category, amount=str(amount), month=month_key)
            db.session.add(budget)

        db.session.commit()
        return jsonify({"budget": budget.to_dict()}), 201

    # ============ LOAN ROUTES ============
    @app.route("/api/loans", methods=["GET", "POST"])
    @login_required
    def loans():
        if request.method == "GET":
            rows = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.created_at.desc()).all()
            return jsonify({"loans": [l.to_dict() for l in rows]})

        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        principal = money(data.get("principal", 0))
        interest_rate = money(data.get("interest_rate", 0))
        currency = (data.get("currency") or "USD").upper()
        account_id = data.get("account_id")

        if not name:
            return jsonify({"error": "Loan name is required."}), 400
        if principal <= 0:
            return jsonify({"error": "Principal must be positive."}), 400
        if currency not in EXCHANGE_RATES:
            return jsonify({"error": "Unsupported currency."}), 400

        loan = Loan(
            user_id=current_user.id,
            name=name,
            principal=str(principal),
            remaining_amount=str(principal),
            interest_rate=str(interest_rate),
            currency=currency,
            account_id=account_id,
            status="active",
            created_at=datetime.utcnow(),
        )
        db.session.add(loan)
        db.session.add(Transaction(
            user_id=current_user.id,
            type="loan_created",
            account_id=account_id,
            amount=str(principal),
            description=f"Loan created: {name}",
            date=datetime.utcnow(),
        ))
        db.session.commit()
        return jsonify({"loan": loan.to_dict()}), 201

    @app.route("/api/loans/<int:loan_id>/payments", methods=["GET", "POST"])
    @login_required
    def loan_payments(loan_id):
        loan = Loan.query.filter_by(id=loan_id, user_id=current_user.id).first()
        if not loan:
            return jsonify({"error": "Loan not found."}), 404

        if request.method == "GET":
            rows = LoanPayment.query.filter_by(loan_id=loan.id).order_by(LoanPayment.payment_date.desc()).all()
            return jsonify({"payments": [p.to_dict() for p in rows]})

        data = request.get_json(silent=True) or {}
        amount = money(data.get("amount", 0))
        account_id = data.get("account_id")

        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400

        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            return jsonify({"error": "Account not found."}), 404

        current_balance = Decimal(account.balance or "0.00")
        if amount > current_balance:
            return jsonify({"error": "Insufficient funds."}), 400

        remaining = Decimal(loan.remaining_amount or "0.00")
        if amount > remaining:
            return jsonify({"error": "Payment exceeds remaining balance."}), 400

        if loan.currency != account.currency:
            amount = convert_amount(amount, account.currency, loan.currency)

        loan.remaining_amount = str(remaining - amount)
        if Decimal(loan.remaining_amount) <= 0:
            loan.status = "paid"
            loan.remaining_amount = "0.00"

        account.balance = str(current_balance - amount)
        payment = LoanPayment(loan_id=loan.id, amount=str(amount), payment_date=datetime.utcnow())
        db.session.add(payment)
        db.session.add(Transaction(
            user_id=current_user.id,
            type="loan_payment",
            account_id=account.id,
            loan_id=loan.id,
            amount=str(amount),
            description=f"Loan payment: {loan.name}",
            date=datetime.utcnow(),
        ))
        db.session.commit()
        return jsonify({"loan": loan.to_dict(), "payment": payment.to_dict()}), 201

    # ============ REPORT ROUTES ============
    @app.route("/api/reports/<int:year>/<int:month>", methods=["GET"])
    @login_required
    def reports(year, month):
        month_key = f"{year}-{str(month).zfill(2)}"
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        filtered = [e for e in expenses if e.date.strftime("%Y-%m") == month_key]
        categories = {}
        for e in filtered:
            categories[e.category] = categories.get(e.category, Decimal("0.00")) + Decimal(e.amount or "0.00")

        budgets = Budget.query.filter_by(user_id=current_user.id, month=month_key).all()
        budget_report = []
        for budget in budgets:
            spent = categories.get(budget.category, Decimal("0.00"))
            budget_amount = Decimal(budget.amount or "0.00")
            percent_used = min(float((spent / budget_amount) * 100) if budget_amount > 0 else 0, 100)
            budget_report.append({
                "category": budget.category,
                "budget": float(budget_amount),
                "spent": float(spent),
                "remaining": float(budget_amount - spent),
                "percent_used": percent_used,
            })

        return jsonify({
            "year": year,
            "month": month,
            "expenses": [e.to_dict() for e in sorted(filtered, key=lambda x: x.date, reverse=True)],
            "budget_report": budget_report,
            "chart": {
                "labels": list(categories.keys()),
                "values": [float(v) for v in categories.values()],
            },
        })

    @app.route("/api/reports/<int:year>/<int:month>/pdf", methods=["GET"])
    @login_required
    def export_report_pdf(year, month):
        resp = reports(year, month)
        payload = resp.get_json()
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        story.append(Paragraph(f"Finance Report - {year}-{month:02d}", styles["Title"]))
        story.append(Spacer(1, 0.3 * 25))

        budget_rows = [["Category", "Budget", "Spent", "Remaining"]]
        for item in payload.get("budget_report", []):
            budget_rows.append([
                item["category"],
                f"${item['budget']:.2f}",
                f"${item['spent']:.2f}",
                f"${item['remaining']:.2f}",
            ])

        if len(budget_rows) > 1:
            table = Table(budget_rows)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3 * 25))

        expense_rows = [["Date", "Category", "Description", "Amount"]]
        for item in payload.get("expenses", []):
            expense_rows.append([
                item["date"][:10],
                item["category"],
                item["description"] or "-",
                f"${item['amount']:.2f}",
            ])

        if len(expense_rows) > 1:
            table = Table(expense_rows)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            story.append(table)

        doc.build(story)
        buffer.seek(0)
        return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"finance_report_{year}_{month:02d}.pdf")

    # ============ DASHBOARD ROUTES ============
    @app.route("/api/dashboard", methods=["GET"])
    @login_required
    def dashboard():
        accounts = Account.query.filter_by(user_id=current_user.id).all()
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        loans = Loan.query.filter_by(user_id=current_user.id).all()

        account_data = [a.to_dict() for a in accounts]
        expense_summary = {}
        for expense in expenses:
            expense_summary[expense.category] = expense_summary.get(expense.category, Decimal("0.00")) + Decimal(expense.amount or "0.00")

        totals = {
            "usd": sum((Decimal(a.balance or "0.00") for a in accounts if a.currency == "USD"), Decimal("0.00")),
            "eur": sum((Decimal(a.balance or "0.00") for a in accounts if a.currency == "EUR"), Decimal("0.00")),
            "loan_total": sum((Decimal(l.remaining_amount or "0.00") for l in loans), Decimal("0.00")),
            "expenses_by_category": {key: float(value) for key, value in expense_summary.items()},
        }

        return jsonify({"accounts": account_data, "totals": {k: float(v) for k, v in totals.items()}})

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error."}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
