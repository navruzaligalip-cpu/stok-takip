const express = require('express');
const { v4: uuidv4 } = require('uuid');
const db      = require('../db/database');
const router  = express.Router();

router.get('/', (req, res) => {
  const { search, category, active = '1', sort = 'name', order = 'asc' } = req.query;
  const allowed = ['name','sku','quantity','buy_price','sell_price','created_at'];
  const col = allowed.includes(sort) ? `p.${sort}` : 'p.name';
  const dir = order === 'desc' ? 'DESC' : 'ASC';
  let sql = `SELECT p.*, c.name as category_name, c.color as category_color, s.name as supplier_name FROM products p LEFT JOIN categories c ON c.id=p.category_id LEFT JOIN suppliers s ON s.id=p.supplier_id WHERE 1=1`;
  const params = [];
  if (active !== 'all') { sql += ' AND p.active=?'; params.push(Number(active)); }
  if (category) { sql += ' AND p.category_id=?'; params.push(category); }
  if (search) { sql += ' AND (p.name LIKE ? OR p.sku LIKE ? OR p.barcode LIKE ?)'; const q = `%${search}%`; params.push(q, q, q); }
  sql += ` ORDER BY ${col} ${dir}`;
  const products = db.prepare(sql).all(...params);
  res.json({ success: true, data: products, total: products.length });
});

router.get('/:id', (req, res, next) => {
  const p = db.prepare(`SELECT p.*, c.name as category_name, s.name as supplier_name FROM products p LEFT JOIN categories c ON c.id=p.category_id LEFT JOIN suppliers s ON s.id=p.supplier_id WHERE p.id=?`).get(req.params.id);
  if (!p) { const e = new Error('Urun bulunamadi'); e.status = 404; return next(e); }
  res.json({ success: true, data: p });
});

router.post('/', (req, res, next) => {
  const { sku, name, barcode, category_id, supplier_id, unit='adet', buy_price=0, sell_price=0, vat_rate=18, quantity=0, min_threshold=5, max_threshold=null, location, description } = req.body;
  if (!sku || !name) { const e = new Error('SKU ve urun adi zorunludur'); e.status = 400; return next(e); }
  const id = uuidv4();
  try {
    db.prepare(`INSERT INTO products (id,sku,name,barcode,category_id,supplier_id,unit,buy_price,sell_price,vat_rate,quantity,min_threshold,max_threshold,location,description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(id, sku, name, barcode||null, category_id||null, supplier_id||null, unit, buy_price, sell_price, vat_rate, quantity, min_threshold, max_threshold||null, location||null, description||null);
    if (quantity > 0) db.prepare(`INSERT INTO stock_movements (id,product_id,type,quantity,prev_quantity,new_quantity,unit_price,total_amount,notes,user_name) VALUES (?,?,?,?,?,?,?,?,?,?)`).run(uuidv4(), id, 'in', quantity, 0, quantity, buy_price, quantity * buy_price, 'Baslangic stogu', 'Sistem');
    res.status(201).json({ success: true, data: db.prepare('SELECT * FROM products WHERE id=?').get(id) });
  } catch (err) {
    if (err.message.includes('UNIQUE')) { const e = new Error('SKU veya barkod zaten kullanimda'); e.status = 409; return next(e); }
    next(err);
  }
});

router.put('/:id', (req, res, next) => {
  const p = db.prepare('SELECT id FROM products WHERE id=?').get(req.params.id);
  if (!p) { const e = new Error('Urun bulunamadi'); e.status = 404; return next(e); }
  const { sku, name, barcode, category_id, supplier_id, unit, buy_price, sell_price, vat_rate, min_threshold, max_threshold, location, description, active } = req.body;
  try {
    db.prepare(`UPDATE products SET sku=COALESCE(?,sku), name=COALESCE(?,name), barcode=?, category_id=?, supplier_id=?, unit=COALESCE(?,unit), buy_price=COALESCE(?,buy_price), sell_price=COALESCE(?,sell_price), vat_rate=COALESCE(?,vat_rate), min_threshold=COALESCE(?,min_threshold), max_threshold=?, location=?, description=?, active=COALESCE(?,active), updated_at=CURRENT_TIMESTAMP WHERE id=?`).run(sku||null, name||null, barcode||null, category_id||null, supplier_id||null, unit||null, buy_price??null, sell_price??null, vat_rate??null, min_threshold??null, max_threshold??null, location||null, description||null, active??null, req.params.id);
    res.json({ success: true, data: db.prepare('SELECT * FROM products WHERE id=?').get(req.params.id) });
  } catch (err) {
    if (err.message.includes('UNIQUE')) { const e = new Error('SKU veya barkod zaten kullanimda'); e.status = 409; return next(e); }
    next(err);
  }
});

router.delete('/:id', (req, res, next) => {
  const p = db.prepare('SELECT id FROM products WHERE id=?').get(req.params.id);
  if (!p) { const e = new Error('Urun bulunamadi'); e.status = 404; return next(e); }
  db.prepare('UPDATE products SET active=0, updated_at=CURRENT_TIMESTAMP WHERE id=?').run(req.params.id);
  res.json({ success: true, message: 'Urun pasif yapildi' });
});

module.exports = router;
