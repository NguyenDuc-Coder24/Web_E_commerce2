const API_BASE = 'http://127.0.0.1:5000/api';

function getToken() { return localStorage.getItem('token') || ''; }
function getUser() { return JSON.parse(localStorage.getItem('user') || 'null'); }

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || 'API Error');
  return data;
}

function showToast(message, error = false) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.style.background = error ? '#dc2626' : '#0f172a';
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}

function getCart() { return JSON.parse(localStorage.getItem('cart') || '[]'); }
function setCart(cart) { localStorage.setItem('cart', JSON.stringify(cart)); }
