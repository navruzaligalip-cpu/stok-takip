const app = require('./src/app');

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`\n  ✅ Stok Takip API çalışıyor → http://localhost:${PORT}`);
  console.log(`  📦 Sağlık kontrolü       → http://localhost:${PORT}/api/health\n`);
});
