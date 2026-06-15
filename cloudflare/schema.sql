-- AI 外贸工作平台 - Cloudflare D1 数据库初始化
-- D1 使用 SQLite 语法

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'operator',
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 客户表
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    name_en TEXT,
    country TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    website TEXT,
    address TEXT,
    tax_id TEXT,
    credit_rating TEXT DEFAULT 'medium',
    credit_score INTEGER DEFAULT 700,
    notes TEXT,
    tags TEXT DEFAULT '[]',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 供应商表
CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    name_en TEXT,
    country TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    factory_address TEXT,
    main_products TEXT,
    certifications TEXT DEFAULT '[]',
    rating INTEGER DEFAULT 3,
    notes TEXT,
    tags TEXT DEFAULT '[]',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    name_en TEXT,
    category TEXT,
    specification TEXT,
    unit TEXT,
    hs_code TEXT,
    hs_code_recommended TEXT,
    supplier_id TEXT REFERENCES suppliers(id),
    moq REAL,
    price_range TEXT,
    images TEXT DEFAULT '[]',
    notes TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 询价表
CREATE TABLE IF NOT EXISTS inquiries (
    id TEXT PRIMARY KEY,
    customer_id TEXT REFERENCES customers(id),
    product_id TEXT REFERENCES products(id),
    quantity REAL,
    unit TEXT,
    target_price REAL,
    currency TEXT DEFAULT 'USD',
    supplier_quotes TEXT DEFAULT '[]',
    ai_analysis TEXT,
    valid_until TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 合同表
CREATE TABLE IF NOT EXISTS contracts (
    id TEXT PRIMARY KEY,
    contract_no TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    customer_id TEXT REFERENCES customers(id),
    supplier_id TEXT REFERENCES suppliers(id),
    amount REAL,
    currency TEXT DEFAULT 'USD',
    sign_date TEXT,
    expiry_date TEXT,
    delivery_date TEXT,
    key_terms TEXT,
    ai_extracted_terms TEXT DEFAULT '{}',
    payment_terms TEXT,
    attachments TEXT DEFAULT '[]',
    notes TEXT,
    status TEXT DEFAULT 'active',
    risk_level TEXT DEFAULT 'low',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_no TEXT UNIQUE NOT NULL,
    customer_id TEXT REFERENCES customers(id),
    contract_id TEXT REFERENCES contracts(id),
    total_amount REAL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'draft',
    production_deadline TEXT,
    shipping_deadline TEXT,
    delivery_deadline TEXT,
    ai_risk_alert TEXT DEFAULT 'low',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 订单项表
CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(id),
    product_id TEXT REFERENCES products(id),
    product_name TEXT,
    specification TEXT,
    quantity REAL,
    unit TEXT,
    unit_price REAL,
    total_price REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 验货表
CREATE TABLE IF NOT EXISTS inspections (
    id TEXT PRIMARY KEY,
    order_id TEXT REFERENCES orders(id),
    inspection_date TEXT,
    inspector TEXT,
    company TEXT,
    result TEXT DEFAULT 'pending',
    ai_result TEXT,
    ai_anomalies TEXT DEFAULT '[]',
    defects TEXT,
    report_url TEXT,
    attachments TEXT DEFAULT '[]',
    notes TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 装运表
CREATE TABLE IF NOT EXISTS shipments (
    id TEXT PRIMARY KEY,
    order_id TEXT REFERENCES orders(id),
    vessel_name TEXT,
    voyage_no TEXT,
    container_no TEXT,
    bl_no TEXT,
    etd TEXT,
    eta TEXT,
    port_of_loading TEXT,
    port_of_discharge TEXT,
    ai_extracted_data TEXT DEFAULT '{}',
    attachments TEXT DEFAULT '[]',
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 收付款表
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    order_id TEXT REFERENCES orders(id),
    receivable REAL,
    received REAL,
    outstanding REAL,
    status TEXT DEFAULT 'unpaid',
    due_date TEXT,
    received_date TEXT,
    payment_method TEXT,
    bank_info TEXT,
    ai_credit_assessment TEXT,
    notes TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    category TEXT,
    ai_category TEXT,
    ai_confidence REAL,
    related_module TEXT,
    related_id TEXT,
    customer_id TEXT REFERENCES customers(id),
    file_path TEXT,
    file_size INTEGER,
    mime_type TEXT,
    ocr_text TEXT,
    ai_extracted_data TEXT DEFAULT '{}',
    ai_embedding TEXT,
    tags TEXT DEFAULT '[]',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    module TEXT,
    record_id TEXT,
    action TEXT,
    detail TEXT DEFAULT '{}',
    ip_address TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 系统设置表
CREATE TABLE IF NOT EXISTS system_settings (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(module, key)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_orders_order_no ON orders(order_no);
CREATE INDEX IF NOT EXISTS idx_contracts_contract_no ON contracts(contract_no);
CREATE INDEX IF NOT EXISTS idx_shipments_bl_no ON shipments(bl_no);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at);
