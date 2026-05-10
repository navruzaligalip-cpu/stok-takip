const express = require('express');
const { v4: uuidv4 } = require('uuid');
const db      = require('../db/database');
const router  = express.Router();

router.get('/', (req, res) => {
  const { product_id, type, from, to, limit = 100, offset = 0 } = req.query;
  let sql = `SELECT m.*, p.name as product_name, p.unit, p.sku FROM stock_movements m JOIN products p ON p.id=m.product_id WHERE 1=1`;
  const params = [];
  if (product_id) { sql += ' AND m.product_id=?'; params.push(product_id); }
  if (type) { sql += ' AND m.type=?'; params.push(type); }
  if (from) { sql += ' AND DATE(m.created_at)>=DATE(?)'; params.push(from); }
  if (to) { sql += ' AND DATE(m.created_at)<=DATE(?)'; params.push(to); }
  sql += ' ORDER BY m.created_at DESC LIMIT ? OFFSET ?';
  params.push(Number(limit), Number(offset));
  const movements = db.prepare(sql).all(...params);
  res.json({ success: true, data: movements, total: movements.length });
});

router.post('/', (req, res, next) => {
  const { product_id, type, quantity, unit_price, document_no, notes, user_name = 'Admin' } = req.body;
  if (!product_id || !type || !quantity) { const e = new Error('Urun, tip ve miktar zorunludur'); e.status = 400; return next(e); }
  if (!['in','out','return','adjustment','transfer'].includes(type)) { const e = new Error('Gecersiz hareket tipi'); e.status = 400; return next(e); }
  const product = db.prepare('SELECT id, quantity, buy_price, sell_price FROM products WHERE id=? AND active=1').get(product_id);
  if (!product) { const e = new Error('Urun bulunamadi'); e.status = 404; return next(e); }
  const qty = Number(quantity);
  const prev = product.quantity;
  let newQty;
  if (type === 'in' || type === 'return') newQty = prev + qty;
  else if (type === 'out') { if (qty > prev) { const e = new Error(`Yetersiz stok. Mevcut: ${prev}`); e.status = 400; return next(e); } newQty = prev - qty; }
  else if (type === 'adjustment') newQty = qty;
  else newQty = prev - qty;
  const price = unit_price ?? (type === 'in' ? product.buy_price : product.sell_price);
  const total = price ? qty * price : null;
  const id = uuidv4();
  const insertMovement = db.transaction(() => {
    db.prepare(`INSERT INTO stock_movements (id,product_id,type,quantity,prev_quantity,new_quantity,unit_price,total_amount,document_no,notes,user_name) VALUES (?,?,?,?,?,?,?,?,?,?,?)`).run(id, product_id, type, qty, prev, newQty, price||null, total||null, document_no||null, notes||null, user_name);
    db.prepare('UPDATE products SET quantity=?, updated_at=CURRENT_TIMESTAMP WHERE id=?').run(newQty, product_id);
  });
  insertMovement();
  const created = db.prepare(`SELECT m.*, p.name as product_name, p.unit FROM stock_movements m JOIN products p ON p.id=m.product_id WHERE m.id=?`).get(id);
  res.status(201).json({ success: true, data: created });
});

module.exports = router;
