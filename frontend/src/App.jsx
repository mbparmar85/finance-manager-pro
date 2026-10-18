import { useEffect, useState, createContext, useContext } from 'react';
import { Link, Navigate, Outlet, Route, Routes, useNavigate } from 'react-router-dom';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const API = '/api';
const CATEGORIES = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Insurance', 'Education', 'Other'];
const AuthContext = createContext(null);

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }

  return data;
}

function useAuth() {
  return useContext(AuthContext);
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading-state">Loading your dashboard...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    apiRequest('/me')
      .then((data) => setUser(data.user))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const handleLogin = (userData) => setUser(userData);

  const handleLogout = async () => {
    try {
      await apiRequest('/logout', { method: 'POST' });
    } finally {
      setUser(null);
      navigate('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ user, setUser: handleLogin, loading, logout: handleLogout }}>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
        <Route path="/register" element={user ? <Navigate to="/" replace /> : <RegisterPage />} />

        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<DashboardPage />} />
          <Route path="accounts" element={<AccountsPage />} />
          <Route path="expenses" element={<ExpensesPage />} />
          <Route path="budgets" element={<BudgetsPage />} />
          <Route path="loans" element={<LoansPage />} />
          <Route path="reports" element={<ReportsPage />} />
        </Route>
      </Routes>
    </AuthContext.Provider>
  );
}

function Layout() {
  const { user, logout } = useAuth();

  return (
    <>
      <nav className="topbar">
        <div className="container nav-inner">
          <div className="brand-wrap">
            <span className="brand-mark">F</span>
            <div>
              <strong>Finance Manager</strong>
              <small>Smart budget control</small>
            </div>
          </div>

          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/accounts">Accounts</Link>
            <Link to="/expenses">Expenses</Link>
            <Link to="/budgets">Budgets</Link>
            <Link to="/loans">Loans</Link>
            <Link to="/reports">Reports</Link>
          </div>

          <button className="logout-button" onClick={logout}>
            Logout · {user?.username}
          </button>
        </div>
      </nav>

      <main className="page-shell">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </>
  );
}

function LoginPage() {
  const { setUser } = useAuth();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await apiRequest('/login', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      setUser(data.user);
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="brand-header">
          <span className="brand-mark large">F</span>
          <div>
            <h2>Welcome back</h2>
            <p>Sign in to your finance workspace</p>
          </div>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="field-group">
            <label>Username</label>
            <input
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="Enter username"
              required
            />
          </div>

          <div className="field-group">
            <label>Password</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Enter password"
              required
            />
          </div>

          <button className="primary-button w-100" type="submit">Login</button>
        </form>

        <div className="auth-footer">
          Need an account? <Link to="/register">Create one</Link>
        </div>
      </div>
    </div>
  );
}

function RegisterPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await apiRequest('/register', { method: 'POST', body: JSON.stringify(form) });
      setSuccess('Registration successful. Redirecting to login...');
      setTimeout(() => navigate('/login'), 1000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="brand-header">
          <span className="brand-mark large">F</span>
          <div>
            <h2>Create account</h2>
            <p>Set up your personal finance dashboard</p>
          </div>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="field-group">
            <label>Username</label>
            <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="Choose a username" required />
          </div>

          <div className="field-group">
            <label>Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="name@example.com" required />
          </div>

          <div className="field-group">
            <label>Password</label>
            <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Minimum 6 characters" required />
          </div>

          <button className="primary-button w-100" type="submit">Create account</button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </div>
      </div>
    </div>
  );
}

function DashboardPage() {
  const [data, setData] = useState({ accounts: [], totals: {} });
  const [chart, setChart] = useState({ labels: [], values: [] });

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiRequest('/dashboard');
        const categoryMap = res.totals.expenses_by_category || {};
        setData(res);
        setChart({
          labels: Object.keys(categoryMap),
          values: Object.values(categoryMap),
        });
      } catch (err) {
        console.error(err);
      }
    };

    load();
  }, []);

  return (
    <div className="dashboard-layout">
      <div className="section-header">
        <div>
          <p className="eyebrow">Overview</p>
          <h3>Financial snapshot</h3>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card blue">
          <span>Total USD</span>
          <strong>${Number(data.totals.usd || 0).toFixed(2)}</strong>
        </div>
        <div className="stat-card purple">
          <span>Total EUR</span>
          <strong>€{Number(data.totals.eur || 0).toFixed(2)}</strong>
        </div>
        <div className="stat-card orange">
          <span>Outstanding loans</span>
          <strong>${Number(data.totals.loan_total || 0).toFixed(2)}</strong>
        </div>
      </div>

      <div className="content-grid">
        <div className="panel">
          <h4>Expense breakdown</h4>
          {chart.labels.length ? (
            <div className="chart-wrap">
              <Doughnut
                data={{
                  labels: chart.labels,
                  datasets: [{
                    data: chart.values,
                    backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316', '#64748b', '#e11d48'],
                  }],
                }}
              />
            </div>
          ) : (
            <p className="muted-text">No expense data yet.</p>
          )}
        </div>

        <div className="panel">
          <h4>Accounts</h4>
          <div className="mini-list">
            {data.accounts.length ? data.accounts.map((account) => (
              <div key={account.id} className="list-row">
                <div>
                  <strong>{account.name}</strong>
                  <small>{account.currency}</small>
                </div>
                <span>{account.currency} {Number(account.balance).toFixed(2)}</span>
              </div>
            )) : <p className="muted-text">No accounts yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

function AccountsPage() {
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState({ name: '', currency: 'USD' });

  const load = async () => {
    const data = await apiRequest('/accounts');
    setAccounts(data.accounts);
  };

  useEffect(() => { load(); }, []);

  const addAccount = async (e) => {
    e.preventDefault();
    await apiRequest('/accounts', { method: 'POST', body: JSON.stringify(form) });
    setForm({ name: '', currency: 'USD' });
    load();
  };

  return (
    <div className="two-column-layout">
      <div className="panel form-panel">
        <h4>Add account</h4>
        <form onSubmit={addAccount} className="stack-form">
          <div className="field-group">
            <label>Account name</label>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Main Checking" required />
          </div>

          <div className="field-group">
            <label>Currency</label>
            <select value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>

          <button className="primary-button" type="submit">Save account</button>
        </form>
      </div>

      <div className="panel">
        <h4>Your accounts</h4>
        <div className="mini-list">
          {accounts.length ? accounts.map((account) => (
            <div key={account.id} className="list-row">
              <div>
                <strong>{account.name}</strong>
                <small>{account.currency}</small>
              </div>
              <span>{account.currency} {Number(account.balance).toFixed(2)}</span>
            </div>
          )) : <p className="muted-text">No accounts yet.</p>}
        </div>
      </div>
    </div>
  );
}

function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState({ account_id: '', category: 'Food', amount: '', description: '' });

  const load = async () => {
    const [expRes, accRes] = await Promise.all([
      apiRequest('/expenses'),
      apiRequest('/accounts'),
    ]);
    setExpenses(expRes.expenses);
    setAccounts(accRes.accounts);
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    await apiRequest('/expenses', { method: 'POST', body: JSON.stringify(form) });
    setForm({ account_id: '', category: 'Food', amount: '', description: '' });
    load();
  };

  return (
    <div className="two-column-layout">
      <div className="panel form-panel">
        <h4>Add expense</h4>
        <form onSubmit={submit} className="stack-form">
          <div className="field-group">
            <label>Account</label>
            <select value={form.account_id} onChange={(e) => setForm({ ...form, account_id: e.target.value })} required>
              <option value="">Select account</option>
              {accounts.map((account) => <option key={account.id} value={account.id}>{account.name}</option>)}
            </select>
          </div>

          <div className="field-group">
            <label>Category</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {CATEGORIES.map((category) => <option key={category} value={category}>{category}</option>)}
            </select>
          </div>

          <div className="field-group">
            <label>Amount</label>
            <input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="0.00" required />
          </div>

          <div className="field-group">
            <label>Description</label>
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Groceries, train pass, etc." />
          </div>

          <button className="primary-button" type="submit">Save expense</button>
        </form>
      </div>

      <div className="panel">
        <h4>Recent spending</h4>
        <div className="mini-list">
          {expenses.length ? expenses.map((expense) => (
            <div key={expense.id} className="list-row">
              <div>
                <strong>{expense.description || expense.category}</strong>
                <small>{expense.category} · {expense.date}</small>
              </div>
              <span className="danger-text">-${Number(expense.amount).toFixed(2)}</span>
            </div>
          )) : <p className="muted-text">No expenses logged yet.</p>}
        </div>
      </div>
    </div>
  );
}

function BudgetsPage() {
  const [budgets, setBudgets] = useState([]);
  const [form, setForm] = useState({ category: 'Food', amount: '', year: new Date().getFullYear(), month: new Date().getMonth() + 1 });

  const load = async () => {
    const data = await apiRequest(`/budgets?year=${form.year}&month=${form.month}`);
    setBudgets(data.budgets);
  };

  useEffect(() => { load(); }, [form.year, form.month]);

  const submit = async (e) => {
    e.preventDefault();
    await apiRequest('/budgets', { method: 'POST', body: JSON.stringify(form) });
    load();
  };

  return (
    <div className="two-column-layout">
      <div className="panel form-panel">
        <h4>Set monthly budget</h4>
        <form onSubmit={submit} className="stack-form">
          <div className="field-group">
            <label>Category</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {CATEGORIES.map((category) => <option key={category} value={category}>{category}</option>)}
            </select>
          </div>

          <div className="field-group">
            <label>Budget amount</label>
            <input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="0.00" required />
          </div>

          <div className="field-group">
            <label>Year</label>
            <input type="number" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} />
          </div>

          <div className="field-group">
            <label>Month</label>
            <input type="number" min="1" max="12" value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} />
          </div>

          <button className="primary-button" type="submit">Save budget</button>
        </form>
      </div>

      <div className="panel">
        <h4>Budget overview</h4>
        <div className="mini-list">
          {budgets.length ? budgets.map((budget) => (
            <div key={budget.id} className="list-row">
              <div>
                <strong>{budget.category}</strong>
                <small>{budget.month}</small>
              </div>
              <span>${Number(budget.amount).toFixed(2)}</span>
            </div>
          )) : <p className="muted-text">No budgets set for this month.</p>}
        </div>
      </div>
    </div>
  );
}

function LoansPage() {
  const [loans, setLoans] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState({ name: '', principal: '', interest_rate: '', currency: 'USD', account_id: '' });

  const load = async () => {
    const [loanRes, accRes] = await Promise.all([
      apiRequest('/loans'),
      apiRequest('/accounts'),
    ]);
    setLoans(loanRes.loans);
    setAccounts(accRes.accounts);
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    await apiRequest('/loans', { method: 'POST', body: JSON.stringify(form) });
    setForm({ name: '', principal: '', interest_rate: '', currency: 'USD', account_id: '' });
    load();
  };

  return (
    <div className="two-column-layout">
      <div className="panel form-panel">
        <h4>Add loan</h4>
        <form onSubmit={submit} className="stack-form">
          <div className="field-group">
            <label>Loan name</label>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Student loan" required />
          </div>

          <div className="field-group">
            <label>Principal</label>
            <input type="number" step="0.01" value={form.principal} onChange={(e) => setForm({ ...form, principal: e.target.value })} placeholder="0.00" required />
          </div>

          <div className="field-group">
            <label>Interest rate</label>
            <input type="number" step="0.01" value={form.interest_rate} onChange={(e) => setForm({ ...form, interest_rate: e.target.value })} placeholder="0.00" />
          </div>

          <div className="field-group">
            <label>Currency</label>
            <select value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>

          <div className="field-group">
            <label>Linked account</label>
            <select value={form.account_id} onChange={(e) => setForm({ ...form, account_id: e.target.value })}>
              <option value="">Optional</option>
              {accounts.map((account) => <option key={account.id} value={account.id}>{account.name}</option>)}
            </select>
          </div>

          <button className="primary-button" type="submit">Add loan</button>
        </form>
      </div>

      <div className="panel">
        <h4>Loan overview</h4>
        <div className="mini-list">
          {loans.length ? loans.map((loan) => (
            <div key={loan.id} className="list-row">
              <div>
                <strong>{loan.name}</strong>
                <small>{loan.status} · {loan.currency}</small>
              </div>
              <span>{loan.currency} {Number(loan.remaining_amount).toFixed(2)}</span>
            </div>
          )) : <p className="muted-text">No loans found.</p>}
        </div>
      </div>
    </div>
  );
}

function ReportsPage() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [report, setReport] = useState({ expenses: [], budget_report: [], chart: { labels: [], values: [] } });

  const load = async () => {
    const data = await apiRequest(`/reports/${year}/${month}`);
    setReport(data);
  };

  useEffect(() => { load(); }, [year, month]);

  const chartData = {
    labels: report.chart.labels,
    datasets: [{
      label: 'Expenses',
      data: report.chart.values,
      backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316', '#64748b', '#e11d48'],
    }],
  };

  return (
    <div className="panel report-panel">
      <div className="section-header compact">
        <div>
          <p className="eyebrow">Reports</p>
          <h3>Monthly analytics</h3>
        </div>
        <a className="primary-button link-button" href={`/api/reports/${year}/${month}/pdf`} target="_blank" rel="noreferrer">Export PDF</a>
      </div>

      <div className="report-controls">
        <div className="field-group inline-field">
          <label>Year</label>
          <input type="number" value={year} onChange={(e) => setYear(e.target.value)} />
        </div>
        <div className="field-group inline-field">
          <label>Month</label>
          <input type="number" min="1" max="12" value={month} onChange={(e) => setMonth(e.target.value)} />
        </div>
      </div>

      <div className="chart-wrap large">
        <Doughnut data={chartData} />
      </div>

      <div className="report-table-wrap">
        <table className="finance-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            {report.expenses.length ? report.expenses.map((item) => (
              <tr key={item.id}>
                <td>{item.date}</td>
                <td>{item.category}</td>
                <td>${Number(item.amount).toFixed(2)}</td>
              </tr>
            )) : (
              <tr>
                <td colSpan="3" className="muted-text">No expense data for this month.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;






















































































































































