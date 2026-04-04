const s3 = document.createElement('script'); s3.src = './js/api.js'; document.head.appendChild(s3);
s3.onload = () => {
  loginForm.onsubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await request('/auth/login', { method:'POST', body: JSON.stringify({ email:email.value, password:password.value }) });
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      showToast('Đăng nhập thành công');
      setTimeout(() => location.href = './index.html', 500);
    } catch (err) { showToast(err.message, true); }
  };
};
