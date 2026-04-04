const s2 = document.createElement('script'); s2.src = './js/api.js'; document.head.appendChild(s2);
s2.onload = async () => {
  const id = new URLSearchParams(location.search).get('id');
  const detail = await request(`/products/${id}`);
  const p = detail.product;

  document.getElementById('productDetail').innerHTML = `<h2>${p.name}</h2><img src="${p.image_url}" style="max-width:420px;width:100%;border-radius:10px"/><p>${p.description || ''}</p><p class="price">${p.price.toLocaleString()}đ</p><button id="addBtn">Thêm vào giỏ</button>`;
  document.getElementById('addBtn').onclick = () => {
    const cart = getCart();
    const f = cart.find(i => i.product_id === p.id);
    if (f) f.quantity += 1; else cart.push({ product_id:p.id, name:p.name, price:p.price, quantity:1 });
    setCart(cart); showToast('Đã thêm vào giỏ hàng');
  };

  document.getElementById('relatedProducts').innerHTML = detail.related_products.map(r => `<a class='card product' href='./product.html?id=${r.id}'><img src='${r.image_url}'/><h4>${r.name}</h4></a>`).join('');
  document.getElementById('reviewList').innerHTML = detail.reviews.map(r => `<p><b>${r.username}</b> (${r.rating}★): ${r.comment || ''}</p>`).join('') || '<p>Chưa có đánh giá.</p>';

  document.getElementById('reviewForm').onsubmit = async (e) => {
    e.preventDefault();
    try {
      await request('/reviews', { method:'POST', body: JSON.stringify({ product_id:Number(id), rating:Number(rating.value), comment:comment.value })});
      showToast('Đã gửi đánh giá');
      setTimeout(()=>location.reload(),500);
    } catch (err) { showToast(err.message, true); }
  };
};
