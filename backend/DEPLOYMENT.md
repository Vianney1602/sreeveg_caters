"""
Production configuration for deploying on Render/Railway/Heroku
"""

# After deploying to a hosting platform:

# 1. CREATE POSTGRESQL DATABASE

# - Render: Add "PostgreSQL" service in dashboard

# - Railway: Add PostgreSQL from marketplace

# - Both will automatically set DATABASE_URL environment variable

# 2. ENVIRONMENT VARIABLES (Set in hosting platform dashboard)

SECRET_KEY=your-production-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/dbname
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ADMIN_USERNAME=admin@yourdomain.com
ADMIN_PASSWORD=YourSecurePassword123!
RAZORPAY_KEY_ID=rzp_live_YOUR_KEY
RAZORPAY_KEY_SECRET=YOUR_SECRET

# 3. RUN DATABASE MIGRATIONS

# SSH into your deployment or use platform CLI:

# flask db upgrade

# 4. SEED THE DATABASE (optional)

# python scripts/seed_db.py

# 5. FRONTEND DEPLOYMENT

# - Deploy frontend to Netlify/Vercel

# - Set REACT_APP_API_URL=https://your-backend-url.onrender.com

# - Set REACT_APP_RAZORPAY_KEY=rzp_live_YOUR_KEY

# - Update axios baseURL in frontend to use REACT_APP_API_URL

# 6. UPDATE CORS

# - Add your frontend domain to CORS_ALLOWED_ORIGINS
