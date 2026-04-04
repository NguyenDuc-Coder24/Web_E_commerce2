const s4 = document.createElement('script'); s4.src = './js/api.js'; document.head.appendChild(s4);
s4.onload = () => {
  registerForm.onsubmit = async (e) => {
    e.preventDefault();
    try {
      await request('/auth/register', { method:'POST', body: JSON.stringify({ username:username.value, email:email.value, password:password.value }) });
      showToast('Đăng ký thành công');
      setTimeout(() => location.href = './login.html', 600);
    } catch (err) { showToast(err.message, true); }
  };
};
