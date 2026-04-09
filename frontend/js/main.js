const s = document.createElement('script'); s.src = './js/api.js'; document.head.appendChild(s);
s.onload = async () => {
  const grid = document.getElementById('productGrid');
  const categorySelect = document.getElementById('categorySelect');

  async function loadCategories() {
    const cats = await request('/categories');
    cats.forEach(c => categorySelect.insertAdjacentHTML('beforeend', `<option value="${c.id}">${c.name}</option>`));
  }

  function card(p) {
    return `<article class="card product"><img src="${p.image_url}" alt="${p.name}"><h3>${p.name}</h3><p class="price">${p.price.toLocaleString()}đ</p><p class="muted">${p.category_name || ''} • ⭐ ${p.avg_rating} (${p.review_count})</p><p class="muted">Đã bán: ${p.total_sold}</p><div class="row"><a class="btn" href="./product.html?id=${p.id}">Chi tiết</a><button onclick='addToCart(${JSON.stringify(p)})'>Thêm giỏ</button></div></article>`;
  }

  window.addToCart = (product) => {
    const cart = getCart();
    const found = cart.find(i => i.product_id === product.id);
    if (found) found.quantity += 1;
    else cart.push({ product_id: product.id, name: product.name, price: product.price, quantity: 1 });
    setCart(cart);
    showToast('Đã thêm vào giỏ hàng');
  };

  async function loadProducts() {
    const q = new URLSearchParams({
      search: document.getElementById('searchInput').value,
      category_id: categorySelect.value,
      min_price: document.getElementById('minPrice').value,
      max_price: document.getElementById('maxPrice').value,
    });
    const products = await request(`/products?${q.toString()}`);
    grid.innerHTML = products.map(card).join('');
  }

  document.getElementById('filterBtn').onclick = loadProducts;
  document.getElementById('searchInput').onkeydown = (e) => {
    if (e.key === 'Enter') loadProducts();
  };
  document.getElementById('searchInput').oninput = () => {
    clearTimeout(window.searchTimer);
    window.searchTimer = setTimeout(loadProducts, 300);
  };
  document.getElementById('logoutBtn').onclick = () => {
    localStorage.removeItem('token'); localStorage.removeItem('user'); showToast('Đã đăng xuất');
  };

  await loadCategories();
  await loadProducts();
  updateCartBadge();
};
