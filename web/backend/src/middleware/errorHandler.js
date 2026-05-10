module.exports = (err, _req, res, _next) => {
  console.error(err.stack);
  const status  = err.status || 500;
  const message = err.message || 'Sunucu hatası';
  res.status(status).json({ success: false, error: message });
};
