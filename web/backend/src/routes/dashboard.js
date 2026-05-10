const express = require('express');
const db      = require('../db/database');
const router  = express.Router();

router.get('/', (_req, res) => {
  const totalProducts  = db.prepare('SELECT COUNT(*) as c FROM products WHERE active=1').get().c;
  const criticalCount  = db.prepare('SELECT COUNT(*) as c FROM products WHERE active=1 AND quantity <= min_threshold').get().c;
  const outOfStock     = db.prepare('SELECT COUNT(*) as c FROM products WHERE active=1 AND quantity <= 0').get().c;
  const totalStockCost = db.prepare('SELECT COALESCE(SUM(quantity*buy_price),0) as v FROM products WHERE active=1').get().v;
  const totalStockSell = db.prepare('SELECT COALESCE(SUM(quantity*sell_price),0) as v FROM products WHERE active=1').get().v;
  const todayIn  = db.prepare("SELECT COALESCE(SUM(total_amount),0) as v FROM stock_movements WHERE type='in' AND DATE(created_at)=DATE('now')").get().v;
  const todayOut = db.prepare("SELECT COALESCE(SUM(total_amount),0) as v FROM stock_movements WHERE type='out' AND DATE(created_at)=DATE('now')").get().v;
  const monthIn  = db.prepare("SELECT COALESCE(SUM(total_amount),0) as v FROM stock_movements WHERE type='in' AND strftime('%Y-%m',created_at)=strftime('%Y-%m','now')").get().v;
  const monthOut = db.prepare("SELECT COALESCE(SUM(total_amount),0) as v FROM stock_movements WHERE type='out' AND strftime('%Y-%m',created_at)=strftime('%Y-%m','now')").get().v;

  const recentMovements = db.prepare(`SELECT m.id, m.type, m.quantity, m.total_amount, m.created_at, m.notes, p.name as product_name, p.unit FROM stock_movements m JOIN products p ON p.id=m.product_id ORDER BY m.created_at DESC LIMIT 5`).all();
  const criticalProducts = db.prepare(`SELECT p.id, p.sku, p.name, p.quantity, p.min_threshold, p.unit, c.name as category FROM products p LEFT JOIN categories c ON c.id=p.category_id WHERE p.active=1 AND p.quantity <= p.min_threshold ORDER BY p.quantity ASC LIMIT 10`).all();
  const weeklyChart = db.prepare(`SELECT DATE(created_at) as date, SUM(CASE WHEN type='in' THEN COALESCE(total_amount,0) ELSE 0 END) as income, SUM(CASE WHEN type='out' THEN COALESCE(total_amount,0) ELSE 0 END) as expense FROM stock_movements WHERE created_at >= DATE('now','-6 days') GROUP BY DATE(created_at) ORDER BY date ASC`).all();
  const categoryChart = db.prepare(`SELECT c.name as category, c.color, COALESCE(SUM(p.quantity*p.buy_price),0) as value FROM categories c LEFT JOIN products p ON p.category_id=c.id AND p.active=1 GROUP BY c.id ORDER BY value DESC`).all();

  res.json({ success: true, data: { stats: { totalProducts, criticalCount, outOfStock, totalStockCost, totalStockSell, profit: totalStockSell - totalStockCost, todayIn, todayOut, monthIn, monthOut }, recentMovements, criticalProducts, weeklyChart, categoryChart } });
});

module.exports = router;
