const s5 = document.createElement('script'); s5.src = './js/api.js'; document.head.appendChild(s5);
s5.onload = () => {
  let discount = 0;

  function renderCart() {
    const cart = getCart();
    const subtotal = cart.reduce((sum, i) => sum + i.price * i.quantity, 0);
    const total = subtotal * (100 - discount) / 100;
    cartItems.innerHTML = cart.map((i, idx) => `<div class='row'><span>${i.name} x ${i.quantity}</span><div><button onclick='inc(${idx})'>+</button><button onclick='dec(${idx})'>-</button><button onclick='delItem(${idx})'>X</button></div></div>`).join('') || '<p>Giỏ hàng trống</p>';
    cartItems.insertAdjacentHTML('beforeend', `<hr><p>Tạm tính: <b>${subtotal.toLocaleString()}đ</b></p><p>Tổng thanh toán: <b>${total.toLocaleString()}đ</b></p>`);
  }

  window.inc = (i)=>{ const c=getCart(); c[i].quantity++; setCart(c); renderCart(); };
  window.dec = (i)=>{ const c=getCart(); c[i].quantity=Math.max(1,c[i].quantity-1); setCart(c); renderCart(); };
  window.delItem = (i)=>{ const c=getCart(); c.splice(i,1); setCart(c); renderCart(); };

  paymentMethod.onchange = () => {
    bankNote.style.display = paymentMethod.value === 'bank_transfer' ? 'block' : 'none';
  };

  applyCouponBtn.onclick = async () => {
    try {
      const r = await request('/coupons/validate', { method:'POST', body: JSON.stringify({ code: coupon.value }) });
      discount = r.discount_percent;
      couponResult.textContent = `Áp dụng thành công: giảm ${discount}%`;
      renderCart();
    } catch (err) { couponResult.textContent = err.message; }
  };

  checkoutForm.onsubmit = async (e) => {
    e.preventDefault();
    try {
      await request('/orders', { method:'POST', body: JSON.stringify({ items:getCart(), address:address.value, phone:phone.value, payment_method:paymentMethod.value, coupon_code:coupon.value }) });
      localStorage.removeItem('cart');
      showToast('Đặt hàng thành công');
      setTimeout(()=>location.href='./profile.html',600);
    } catch (err) { showToast(err.message, true); }
  };

  renderCart();
  paymentMethod.onchange();
  updateCartBadge();
};
