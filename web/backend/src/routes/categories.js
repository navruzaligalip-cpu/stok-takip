const express = require('express');
const { v4: uuidv4 } = require('uuid');
const db      = require('../db/database');
const router  = express.Router();

router.get('/', (_req, res) => {
  const rows = db.prepare(`
    SELECT c.*, COUNT(p.id) as product_count
    FROM categories c
    LEFT JOIN products p ON p.category_id=c.id AND p.active=1
    GROUP BY c.id ORDER BY c.name
  `).all();
  res.json({ success: true, data: rows });
});

router.post('/', (req, res, next) => {
  const { name, color = '#6366f1' } = req.body;
  if (!name) { const e = new Error('Kategori adı zorunludur'); e.status = 400; return next(e); }
  const id = uuidv4();
  try {
    db.prepare('INSERT INTO categories (id,name,color) VALUES (?,?,?)').run(id, name, color);
    res.status(201).json({ success: true, data: db.prepare('SELECT * FROM categories WHERE id=?').get(id) });
  } catch {
    const e = new Error('Bu kategori adı zaten kullanılıyor'); e.status = 409; next(e);
  }
});

router.put('/:id', (req, res, next) => {
  const { name, color } = req.body;
  const c = db.prepare('SELECT id FROM categories WHERE id=?').get(req.params.id);
  if (!c) { const e = new Error('Kategori bulunamadı'); e.status = 404; return next(e); }
  db.prepare('UPDATE categories SET name=COALESCE(?,name), color=COALESCE(?,color) WHERE id=?')
    .run(name||null, color||null, req.params.id);
  res.json({ success: true, data: db.prepare('SELECT * FROM categories WHERE id=?').get(req.params.id) });
});

router.delete('/:id', (req, res, next) => {
  const used = db.prepare('SELECT COUNT(*) as c FROM products WHERE category_id=?').get(req.params.id).c;
  if (used > 0) {
    const e = new Error(`Bu kategoride ${used} ürün var. Önce ürünleri taşıyın.`); e.status = 409; return next(e);
  }
  db.prepare('DELETE FROM categories WHERE id=?').run(req.params.id);
  res.json({ success: true, message: 'Kategori silindi' });
});

module.exports = router;
