CREATE DATABASE IF NOT EXISTS ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  role ENUM('guest','user','admin') NOT NULL DEFAULT 'user',
  status ENUM('active','inactive') NOT NULL DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  price DECIMAL(12,2) NOT NULL,
  description TEXT,
  image_url VARCHAR(500),
  stock_quantity INT NOT NULL DEFAULT 0,
  category_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS coupons (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(40) NOT NULL UNIQUE,
  discount_percent INT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  expiry_date DATE NULL
);

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  total_price DECIMAL(12,2) NOT NULL,
  status ENUM('pending','approved','delivering','delivered','cancelled') DEFAULT 'pending',
  address VARCHAR(255) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  payment_method ENUM('cod','bank','bank_transfer') DEFAULT 'cod',
  coupon_code VARCHAR(40) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL,
  price DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id),
  CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_reviews_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO categories (name) VALUES ('Điện thoại'),('Laptop'),('Phụ kiện')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO products (name, price, description, image_url, stock_quantity, category_id) VALUES
('Nova Phone X', 15990000, 'Điện thoại flagship hiệu năng cao', 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200', 20, 1),
('Nova Book Pro', 28990000, 'Laptop mỏng nhẹ cho công việc', 'https://images.unsplash.com/photo-1517336714739-489689fd1ca8?w=1200', 15, 2),
('TWS Nova Buds', 1990000, 'Tai nghe không dây chống ồn', 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=1200', 50, 3)
ON DUPLICATE KEY UPDATE name = VALUES(name);
