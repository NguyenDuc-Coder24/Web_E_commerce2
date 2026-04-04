# E-commerce Website (Flask + Vanilla JS + MySQL)

## 1) Cấu trúc thư mục

```
Web_E_commerce2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── admin.html
│   ├── checkout.html
│   ├── index.html
│   ├── login.html
│   ├── product.html
│   ├── profile.html
│   ├── register.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── admin.js
│       ├── api.js
│       ├── checkout.js
│       ├── login.js
│       ├── main.js
│       ├── product.js
│       ├── profile.js
│       └── register.js
├── sql/
│   └── init.sql
└── README.md
```

## 2) Tính năng chính

- **Guest**: xem danh sách sản phẩm, tìm kiếm/lọc theo danh mục và giá, xem chi tiết, thêm/sửa/xóa giỏ hàng với LocalStorage, checkout với COD/chuyển khoản.
- **User**: đăng ký/đăng nhập bằng JWT, quản lý profile, lịch sử đơn hàng và trạng thái.
- **Admin**: dashboard thống kê doanh thu/đơn hàng/người dùng, CRUD sản phẩm, quản lý đơn hàng, kích hoạt/vô hiệu hóa user, tạo & quản lý coupon.
- **Mở rộng**: rating/comment sau khi mua hàng (đơn đã `delivered`), coupon tại checkout, related products, toast notification.

## 3) Cài đặt và chạy

### Yêu cầu
- Python 3.10+
- MySQL 8+

### Bước 1: Tạo DB
```bash
mysql -u root -p < sql/init.sql
```

### Bước 2: Chạy Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
python run.py
```
Backend chạy tại: `http://127.0.0.1:5000`

### Bước 3: Chạy Frontend
Mở thư mục `frontend/` bằng Live Server hoặc chạy HTTP server:
```bash
cd frontend
python -m http.server 5500
```
Frontend chạy tại: `http://127.0.0.1:5500`

## 4) Tài khoản gợi ý
Bạn có thể insert thêm admin vào MySQL (password đã hash bcrypt từ backend endpoint hoặc script riêng). Cách nhanh:
- Đăng ký user thường qua `register.html`.
- Đổi role user thành `admin` trong DB để vào `admin.html`.

## 5) Security notes
- Password được hash bằng **bcrypt** (`Flask-Bcrypt`).
- ORM SQLAlchemy giúp giảm rủi ro SQL injection.
- API admin có kiểm tra role từ JWT + trạng thái tài khoản.
