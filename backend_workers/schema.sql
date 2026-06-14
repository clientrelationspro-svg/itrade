-- AI 外贸工作平台 - Cloudflare D1 数据库 Schema
-- D1 使用 SQLite 语法

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'user',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 客户表
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_en TEXT,
    country TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    tax_id TEXT,
    notes TEXT,
    tags TEXT,  -- JSON array
    credit_rating TEXT,
    credit_score INTEGER,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 供应商表
CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_en TEXT,
    country TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    factory_address TEXT,
    main_products TEXT,
    certifications TEXT,  -- JSON array
    rating INTEGER DEFAULT 3,
    notes TEXT,
    tags TEXT,  -- JSON array
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_en TEXT,
    category TEXT,
    specification TEXT,
    unit TEXT,
    hs_code TEXT,
    hs_code_recommended TEXT,
    supplier_id TEXT,
    moq REAL,
    price_range TEXT,
    images TEXT,  -- JSON array
    notes TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 询价表
CREATE TABLE IF NOT EXISTS inquiries (
    id TEXT PRIMARY KEY,
    inquiry_no TEXT UNIQUE NOT NULL,
    customer_id TEXT,
    product_id TEXT,
    quantity REAL,
    unit TEXT,
    target_price REAL,
    currency TEXT DEFAULT 'USD',
    supplier_quotes TEXT,  -- JSON array
    valid_until TEXT,
    ai_analysis TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 合同表
CREATE TABLE IF NOT EXISTS contracts (
    id TEXT PRIMARY KEY,
    contract_no TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    customer_id TEXT,
    supplier_id TEXT,
    amount REAL,
    currency TEXT DEFAULT 'USD',
    sign_date TEXT,
    expiry_date TEXT,
    delivery_date TEXT,
    key_terms TEXT,
    payment_terms TEXT,
    attachments TEXT,  -- JSON array
    ai_extracted_terms TEXT,  -- JSON
    risk_level TEXT,
    notes TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_no TEXT UNIQUE NOT NULL,
    customer_id TEXT,
    contract_id TEXT,
    total_amount REAL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'draft',
    production_deadline TEXT,
    shipping_deadline TEXT,
    delivery_deadline TEXT,
    notes TEXT,
    ai_risk_alert TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 订单明细表
CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT,
    product_name TEXT,
    specification TEXT,
    quantity REAL,
    unit TEXT,
    unit_price REAL,
    total_price REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 验货表
CREATE TABLE IF NOT EXISTS inspections (
    id TEXT PRIMARY KEY,
    inspection_no TEXT UNIQUE NOT NULL,
    order_id TEXT,
    inspection_date TEXT,
    inspector TEXT,
    company TEXT,
    result TEXT DEFAULT 'pending',
    defects TEXT,
    report_url TEXT,
    attachments TEXT,  -- JSON array
    ai_result TEXT,
    ai_anomalies TEXT,  -- JSON array
    notes TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 装运表
CREATE TABLE IF NOT EXISTS shipments (
    id TEXT PRIMARY KEY,
    shipment_no TEXT UNIQUE NOT NULL,
    order_id TEXT,
    vessel_name TEXT,
    voyage_no TEXT,
    container_no TEXT,
    bl_no TEXT,
    etd TEXT,
    eta TEXT,
    port_of_loading TEXT,
    port_of_discharge TEXT,
    attachments TEXT,  -- JSON array
    ai_extracted_data TEXT,  -- JSON
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 收付款表
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    payment_no TEXT UNIQUE NOT NULL,
    order_id TEXT,
    receivable REAL,
    received REAL,
    outstanding REAL,
    due_date TEXT,
    received_date TEXT,
    payment_method TEXT,
    bank_info TEXT,
    ai_credit_assessment TEXT,
    notes TEXT,  -- JSON array
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    category TEXT,
    related_module TEXT,
    related_id TEXT,
    customer_id TEXT,
    file_path TEXT,
    file_size INTEGER,
    mime_type TEXT,
    ocr_text TEXT,
    ai_category TEXT,
    ai_confidence REAL,
    ai_extracted_data TEXT,  -- JSON
    tags TEXT,  -- JSON array
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- 系统设置表
CREATE TABLE IF NOT EXISTS system_settings (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(module, key)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);

-- 插入默认管理员用户 (密码: admin123)
INSERT OR IGNORE INTO users (id, username, password_hash, name, role, status)
VALUES ('admin-001', 'admin', '$2b$12$LQv3c1y.bVLEZvrZ3GvWvVWvWvWvWvWvWvWvWvWvWvWvWvWvWvWvWvWvW', '管理员', 'admin', 'active');
