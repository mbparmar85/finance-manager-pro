body {
  margin: 0;
  background: #f5f7fb;
  font-family: 'Inter', sans-serif;
}

#root {
  min-height: 100vh;
}

.auth-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef4ff, #f2f7ff);
}

.auth-card {
  width: min(420px, 92vw);
  padding: 2rem;
  border-radius: 18px;
  box-shadow: 0 14px 40px rgba(13, 110, 253, 0.12);
}

.card {
  border: 1px solid rgba(0, 0, 0, 0.04);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
  padding: 1.25rem;
  background: #fff;
}

.stat-card {
  min-height: 140px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
}

.stat-blue { background: linear-gradient(135deg, #0d6efd, #3b82f6); }
.stat-purple { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }
.stat-red { background: linear-gradient(135deg, #ef4444, #f97316); }

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 0;
  border-bottom: 1px solid #edf1f7;
}

.list-item:last-child {
  border-bottom: none;
}

.navbar {
  padding: 0.9rem 0;
}

.nav-link {
  color: rgba(255,255,255,0.9) !important;
}

.btn-primary {
  background: #0d6efd;
  border-color: #0d6efd;
}

.text-danger {
  color: #dc3545 !important;
}

@media (max-width: 768px) {
  .navbar-nav {
    padding-top: 0.75rem;
  }
}
