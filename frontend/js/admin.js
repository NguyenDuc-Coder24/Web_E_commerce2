const s7 = document.createElement('script'); s7.src = './js/api.js'; document.head.appendChild(s7);
s7.onload = async () => {
  async function load() {
    const d = await request('/admin/dashboard');
    dashboardStats.innerHTML = `<div class='card'>Doanh thu: ${d.total_revenue.toLocaleString()}đ</div><div class='card'>Đơn hàng: ${d.total_orders}</div><div class='card'>Người dùng: ${d.total_users}</div>`;

    const products = await request('/admin/products');
    productTable.innerHTML = products.map(p => `<div class='row'><span>${p.name} (${p.stock_quantity})</span><div><button onclick='delP(${p.id})'>Xóa</button></div></div>`).join('');

    const orders = await request('/admin/orders');
    orderTable.innerHTML = orders.map(o => `<div class='row'><span>#${o.id} - ${o.username} - ${o.status}</span><select onchange='upOrder(${o.id}, this.value)'><option>pending</option><option>approved</option><option>delivering</option><option>delivered</option><option>cancelled</option></select></div>`).join('');

    const users = await request('/admin/users');
    userTable.innerHTML = users.map(u => `<div class='row'><span>${u.username} (${u.status})</span><select onchange='upUser(${u.id}, this.value)'><option>active</option><option>inactive</option></select></div>`).join('');

    const coupons = await request('/admin/coupons');
    couponTable.innerHTML = coupons.map(c => `<div class='row'><span>${c.code} - ${c.discount_percent}% - ${c.is_active ? 'active' : 'inactive'}</span></div>`).join('');
  }

  window.delP = async (id)=>{ await request(`/admin/products/${id}`,{method:'DELETE'}); showToast('Đã xóa'); load(); };
  window.upOrder = async (id,status)=>{ await request(`/admin/orders/${id}/status`,{method:'PUT',body:JSON.stringify({status})}); showToast('Cập nhật đơn hàng'); };
  window.upUser = async (id,status)=>{ await request(`/admin/users/${id}/status`,{method:'PUT',body:JSON.stringify({status})}); showToast('Cập nhật user'); };

  productForm.onsubmit = async (e)=>{
    e.preventDefault();
    await request('/admin/products',{method:'POST',body:JSON.stringify({name:name.value,price:Number(price.value),category_id:Number(category_id.value),stock_quantity:Number(stock_quantity.value),image_url:image_url.value,description:description.value})});
    showToast('Đã thêm sản phẩm'); productForm.reset(); load();
  };

  couponForm.onsubmit = async (e)=>{
    e.preventDefault();
    await request('/admin/coupons',{method:'POST',body:JSON.stringify({code:code.value,discount_percent:Number(discount_percent.value),expiry_date:expiry_date.value || null,is_active:true})});
    showToast('Đã tạo coupon'); couponForm.reset(); load();
  };

  try { await load(); } catch(err) { showToast(err.message, true); }
};
