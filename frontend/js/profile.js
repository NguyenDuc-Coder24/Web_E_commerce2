const s6 = document.createElement('script'); s6.src = './js/api.js'; document.head.appendChild(s6);
s6.onload = async () => {
  try {
    const me = await request('/me');
    username.value = me.username; email.value = me.email;
    const orders = await request('/orders/my');
    orderHistory.innerHTML = orders.map(o => `<div class='card'><b>#${o.id}</b> - <span class='badge'>${o.status}</span> - ${o.total_price.toLocaleString()}đ ${o.items.map(i=>`<p>${i.product_name} x ${i.quantity}</p>`).join('')}</div>`).join('') || '<p>Chưa có đơn hàng.</p>';
  } catch { showToast('Vui lòng đăng nhập', true); }

  profileForm.onsubmit = async (e) => {
    e.preventDefault();
    try { await request('/me', { method:'PUT', body: JSON.stringify({ username:username.value, email:email.value })}); showToast('Cập nhật thành công'); }
    catch (err) { showToast(err.message, true); }
  };
};
