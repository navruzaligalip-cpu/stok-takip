const Database = require('better-sqlite3');
const path     = require('path');

const DB_PATH = path.join(__dirname, '..', '..', 'stok.db');
const db = new Database(DB_PATH);

db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

db.exec(`
  CREATE TABLE IF NOT EXISTS categories (
    id         TEXT    PRIMARY KEY,
    name       TEXT    NOT NULL UNIQUE,
    color      TEXT    NOT NULL DEFAULT '#6366f1',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS suppliers (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    phone      TEXT,
    email      TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS products (
    id            TEXT    PRIMARY KEY,
    sku           TEXT    NOT NULL UNIQUE,
    name          TEXT    NOT NULL,
    barcode       TEXT    UNIQUE,
    category_id   TEXT    REFERENCES categories(id) ON DELETE SET NULL,
    supplier_id   TEXT    REFERENCES suppliers(id)  ON DELETE SET NULL,
    unit          TEXT    NOT NULL DEFAULT 'adet',
    buy_price     REAL    NOT NULL DEFAULT 0,
    sell_price    REAL    NOT NULL DEFAULT 0,
    vat_rate      REAL    NOT NULL DEFAULT 18,
    quantity      REAL    NOT NULL DEFAULT 0,
    min_threshold REAL    NOT NULL DEFAULT 5,
    max_threshold REAL,
    location      TEXT,
    description   TEXT,
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS stock_movements (
    id            TEXT PRIMARY KEY,
    product_id    TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    type          TEXT NOT NULL CHECK(type IN ('in','out','return','adjustment','transfer')),
    quantity      REAL NOT NULL,
    prev_quantity REAL NOT NULL,
    new_quantity  REAL NOT NULL,
    unit_price    REAL,
    total_amount  REAL,
    document_no   TEXT,
    notes         TEXT,
    user_name     TEXT DEFAULT 'Admin',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX IF NOT EXISTS idx_products_category  ON products(category_id);
  CREATE INDEX IF NOT EXISTS idx_movements_product  ON stock_movements(product_id);
  CREATE INDEX IF NOT EXISTS idx_movements_type     ON stock_movements(type);
  CREATE INDEX IF NOT EXISTS idx_movements_date     ON stock_movements(created_at);
`);

const seedCount = db.prepare('SELECT COUNT(*) as c FROM categories').get().c;

if (seedCount === 0) {
  const { v4: uuidv4 } = require('uuid');

  const cats = [
    { id: uuidv4(), name: 'Elektronik',  color: '#6366f1' },
    { id: uuidv4(), name: 'Ofis',        color: '#0ea5e9' },
    { id: uuidv4(), name: 'Temizlik',    color: '#10b981' },
    { id: uuidv4(), name: 'Gıda',        color: '#f59e0b' },
  ];
  const insertCat = db.prepare('INSERT INTO categories (id,name,color) VALUES (?,?,?)');
  cats.forEach(c => insertCat.run(c.id, c.name, c.color));

  const sup = { id: uuidv4(), name: 'ABC Tedarik', phone: '0212-555-0001', email: 'info@abc.com' };
  db.prepare('INSERT INTO suppliers (id,name,phone,email) VALUES (?,?,?,?)').run(sup.id, sup.name, sup.phone, sup.email);

  const products = [
    { id: uuidv4(), sku: 'ELK-001', name: 'Laptop 15"', barcode: '1234567890001', cat: cats[0].id, sup: sup.id, unit: 'adet', buy: 8500, sell: 11000, vat: 20, qty: 15, min: 3 },
    { id: uuidv4(), sku: 'ELK-002', name: 'Kablosuz Klavye', barcode: '1234567890002', cat: cats[0].id, sup: sup.id, unit: 'adet', buy: 150, sell: 250, vat: 20, qty: 2, min: 5 },
    { id: uuidv4(), sku: 'ELK-003', name: 'USB-C Hub 7 Port', barcode: '1234567890003', cat: cats[0].id, sup: sup.id, unit: 'adet', buy: 220, sell: 380, vat: 20, qty: 28, min: 5 },
    { id: uuidv4(), sku: 'OFS-001', name: 'A4 Kagit 500 Yaprak', barcode: '1234567890004', cat: cats[1].id, sup: sup.id, unit: 'paket', buy: 45, sell: 75, vat: 8, qty: 0, min: 10 },
    { id: uuidv4(), sku: 'OFS-002', name: 'Tukenmez Kalem 12li', barcode: '1234567890005', cat: cats[1].id, sup: sup.id, unit: 'kutu', buy: 18, sell: 32, vat: 8, qty: 60, min: 10 },
    { id: uuidv4(), sku: 'TMZ-001', name: 'Sivi Sabun 1L', barcode: '1234567890006', cat: cats[2].id, sup: sup.id, unit: 'litre', buy: 22, sell: 38, vat: 18, qty: 50, min: 8 },
    { id: uuidv4(), sku: 'GDA-001', name: 'Filtre Kahve 250g', barcode: '1234567890007', cat: cats[3].id, sup: sup.id, unit: 'paket', buy: 65, sell: 95, vat: 1, qty: 4, min: 5 },
  ];

  const insertP = db.prepare(`INSERT INTO products (id,sku,name,barcode,category_id,supplier_id,unit,buy_price,sell_price,vat_rate,quantity,min_threshold) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`);
  const insertM = db.prepare(`INSERT INTO stock_movements (id,product_id,type,quantity,prev_quantity,new_quantity,unit_price,total_amount,notes,user_name) VALUES (?,?,?,?,?,?,?,?,?,?)`);

  products.forEach(p => {
    insertP.run(p.id, p.sku, p.name, p.barcode, p.cat, p.sup, p.unit, p.buy, p.sell, p.vat, p.qty, p.min);
    if (p.qty > 0) insertM.run(uuidv4(), p.id, 'in', p.qty, 0, p.qty, p.buy, p.qty * p.buy, 'Baslangic stogu', 'Sistem');
  });

  insertM.run(uuidv4(), products[0].id, 'out', 3, 15, 12, products[0].sell, 3 * products[0].sell, 'Musteri satisi', 'Admin');
  db.prepare('UPDATE products SET quantity=12 WHERE id=?').run(products[0].id);
  insertM.run(uuidv4(), products[5].id, 'out', 8, 50, 42, products[5].sell, 8 * products[5].sell, 'Satis', 'Admin');
  db.prepare('UPDATE products SET quantity=42 WHERE id=?').run(products[5].id);

  console.log('  Seed verisi olusturuldu.');
}

module.exports = db;
