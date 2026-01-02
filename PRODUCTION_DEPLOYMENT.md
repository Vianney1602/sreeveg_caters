# Production Deployment Guide - Hotel Shanmuga Bhavaan

## 🚀 Pre-Deployment Checklist

### Backend

- [x] All API endpoints implemented (20+ routes)
- [x] PostgreSQL database configured
- [x] JWT authentication working
- [x] Razorpay payment integration complete
- [x] Socket.IO real-time updates working
- [x] Error handling and logging in place
- [x] CORS configured
- [x] File upload with validation
- [x] Order status tracking (NEW: GET /api/orders/<id>)

### Frontend

- [x] Menu display from API
- [x] Real-time menu updates via WebSocket
- [x] Shopping cart functionality
- [x] Order checkout with form validation
- [x] Order confirmation modal with order ID
- [x] Payment integration (COD + Razorpay)
- [x] Responsive design

### Database

- [x] PostgreSQL 18 with full schema
- [x] 10 menu items migrated
- [x] 2 event types configured
- [x] 9 customers in database
- [x] 34+ orders with items
- [x] Auto-increment sequences reset

---

## 📋 Environment Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://postgres:YourPassword%40@your-host:5432/cater_db

# JWT
JWT_SECRET_KEY=your-secure-random-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# Admin Credentials
ADMIN_USERNAME=admin@sreeveg.com
ADMIN_PASSWORD=your-strong-password

# Razorpay (Production Keys)
RAZORPAY_KEY_ID=rzp_live_your_production_key
RAZORPAY_KEY_SECRET=your_production_secret

# CORS
CORS_ALLOWED_ORIGINS=https://www.sreevegcaters.com,https://admin.sreevegcaters.com

# Uploads
MAX_CONTENT_LENGTH=5242880
ALLOWED_IMAGE_EXTENSIONS=png,jpg,jpeg,webp
```

### Frontend (.env)

```env
REACT_APP_API_URL=https://api.sreevegcaters.com
REACT_APP_RAZORPAY_KEY=rzp_live_your_production_key
```

---

## 🔧 Deployment Steps

### 1. Backend Deployment (Render/Railway/AWS)

```bash
# Set environment variables in deployment platform dashboard
# DATABASE_URL, JWT_SECRET_KEY, RAZORPAY keys, etc.

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations
python backend/manage.py db upgrade

# Start server with Gunicorn
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 wsgi:app_for_gunicorn
```

### 2. Frontend Deployment (Vercel/Netlify)

```bash
# Build
cd frontend
npm run build

# Deploy the build/ directory to your hosting
```

### 3. Database Setup

```sql
-- Create database (if not exists)
CREATE DATABASE cater_db;

-- Reset sequences (after initial migration)
SELECT setval('customers_customer_id_seq', (SELECT MAX(customer_id) + 1 FROM customers), false);
SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) + 1 FROM orders), false);
SELECT setval('menu_items_item_id_seq', (SELECT MAX(item_id) + 1 FROM menu_items), false);
SELECT setval('order_menu_items_order_menu_id_seq', (SELECT MAX(order_menu_id) + 1 FROM order_menu_items), false);
```

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] Enable HTTPS/SSL certificates
- [ ] Set CORS to specific domains only
- [ ] Enable database backups
- [ ] Use strong Razorpay production keys
- [ ] Implement rate limiting (optional)
- [ ] Set up monitoring/alerts
- [ ] Regular security audits

---

## 📊 API Endpoints Summary

### Menu Management

- `GET /api/menu` - List all menu items
- `POST /api/menu` - Add menu item (Admin)
- `PUT /api/menu/<id>` - Update menu item (Admin)
- `DELETE /api/menu/<id>` - Delete menu item (Admin)

### Orders

- `GET /api/orders` - List all orders (Admin)
- `POST /api/orders` - Create new order
- `GET /api/orders/<id>` - **NEW** Get order details by ID
- `PUT /api/orders/status/<id>` - Update order status (Admin)

### Payments

- `POST /api/payments/create_order` - Create Razorpay order
- `POST /api/payments/verify` - Verify payment

### Customers

- `GET /api/customers` - List customers (Admin)
- `POST /api/customers/register` - Customer registration
- `POST /api/customers/login` - Customer login
- `POST /api/customers/refresh` - Refresh JWT token
- `GET /api/customers/<id>/orders` - Get customer orders

### Admin

- `POST /api/admin/login` - Admin login

### Statistics

- `GET /api/stats/summary` - Dashboard statistics (Admin)

---

## 🚨 Monitoring & Maintenance

### Production Monitoring

- Set up error tracking (Sentry)
- Monitor API response times
- Track database performance
- Set up log aggregation

### Regular Maintenance

- Weekly database backups
- Monthly security audits
- Update dependencies quarterly
- Monitor storage/image uploads

---

## 📱 Testing Before Launch

1. **Test Order Flow**

   - Create order with COD
   - Create order with Razorpay (test card: 4111 1111 1111 1111)
   - Verify order appears in admin panel

2. **Test Menu Management**

   - Add new menu item
   - Verify it appears in real-time on frontend
   - Update/delete item

3. **Test Performance**

   - Load test with concurrent users
   - Check API response times
   - Verify database queries are optimized

4. **Test Payment**
   - Complete full payment flow
   - Verify order status updates
   - Check Razorpay webhook integration

---

## 🆘 Troubleshooting

### Order 500 Error

- Check database sequences are reset
- Verify DATABASE_URL is correct
- Check PostgreSQL connection

### Razorpay Errors

- Verify production keys in .env
- Check API credentials
- Ensure amount is in correct format

### Real-time Updates Not Working

- Verify Socket.IO is enabled
- Check firewall allows WebSocket
- Verify CORS includes frontend domain

---

## 📞 Support & Contact

For issues or questions:

1. Check API logs: `gunicorn` output
2. Check database: `psql` connection test
3. Check frontend console: Browser DevTools
4. Review error traceback in logs

---

**Status**: ✅ READY FOR PRODUCTION
**Last Updated**: December 28, 2025
**Version**: 1.0.0
