const express    = require('express');
const cors       = require('cors');
const helmet     = require('helmet');
const morgan     = require('morgan');

const dashboardRoutes = require('./routes/dashboard');
const productRoutes   = require('./routes/products');
const categoryRoutes  = require('./routes/categories');
const movementRoutes  = require('./routes/movements');
const errorHandler    = require('./middleware/errorHandler');

// Uygulama başlangıcında DB'yi başlat
require('./db/database');

const app = express();

app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors({ origin: '*', methods: ['GET','POST','PUT','PATCH','DELETE'] }));
app.use(morgan('dev'));
app.use(express.json());

app.get('/api/health', (_req, res) =>
  res.json({ status: 'OK', timestamp: new Date().toISOString() })
);

app.use('/api/dashboard',  dashboardRoutes);
app.use('/api/products',   productRoutes);
app.use('/api/categories', categoryRoutes);
app.use('/api/movements',  movementRoutes);

app.use(errorHandler);

module.exports = app;
