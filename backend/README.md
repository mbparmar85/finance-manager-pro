# Finance Manager API

Flask-based REST API for personal finance management.

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Development Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login
- `POST /api/logout` - Logout
- `GET /api/me` - Get current user

### Accounts
- `GET /api/accounts` - List accounts
- `POST /api/accounts` - Create account
- `POST /api/accounts/<id>` - Update account

### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/deposit` - Deposit to account
- `POST /api/withdraw` - Withdraw from account
- `POST /api/transfer` - Transfer between accounts

### Expenses
- `GET /api/expenses` - List expenses
- `POST /api/expenses` - Add expense

### Budgets
- `GET /api/budgets` - List budgets
- `POST /api/budgets` - Set budget

### Loans
- `GET /api/loans` - List loans
- `POST /api/loans` - Create loan
- `GET /api/loans/<id>/payments` - List loan payments
- `POST /api/loans/<id>/payments` - Make loan payment

### Reports
- `GET /api/reports/<year>/<month>` - Get monthly report
- `GET /api/reports/<year>/<month>/pdf` - Export PDF report
- `GET /api/dashboard` - Get dashboard data

## Database

The app uses SQLAlchemy ORM with support for:
- SQLite (development)
- PostgreSQL (production)

Tables are auto-created on startup.

## Production Deployment

See deployment guides:
- [Render.com Guide](../DEPLOY_RENDER.md)
- [Railway Guide](../DEPLOY_RAILWAY.md)
- [VPS Guide](../DEPLOY_VPS.md)
