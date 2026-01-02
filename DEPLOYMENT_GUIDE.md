# Complete Deployment Guide - Hotel Shanmuga Bhavaan

## ✅ Your Website WILL Work on HTTPS!

All modern hosting platforms (Render, Railway, Netlify, Vercel) provide **automatic HTTPS/SSL certificates** for free. Your website will be secure with `https://` URLs.

---

## 🚀 Quick Deployment Steps

### **Option 1: Render.com (Recommended - Easy & Free)**

#### Backend Deployment:

1. **Push your code to GitHub**

   ```bash
   cd H:\cater-main
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/cater-backend.git
   git push -u origin main
   ```

2. **Create Render Account**

   - Go to https://render.com
   - Sign up (free tier available)

3. **Deploy Backend**

   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `cater-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:app`
     - **Instance Type**: Free

4. **Add PostgreSQL Database**

   - Click "New +" → "PostgreSQL"
   - Name: `cater-db`
   - Plan: Free
   - Copy the "Internal Database URL"

5. **Set Environment Variables** (in Render dashboard → Environment)

   ```
   DATABASE_URL=<paste-internal-database-url>
   SECRET_KEY=<generate-with-python-secrets>
   JWT_SECRET_KEY=<generate-with-python-secrets>
   ADMIN_USERNAME=admin@yourdomain.com
   ADMIN_PASSWORD=YourSecurePassword123!
   CORS_ALLOWED_ORIGINS=https://yourfrontend.netlify.app
   RAZORPAY_KEY_ID=rzp_live_YOUR_KEY
   RAZORPAY_KEY_SECRET=YOUR_SECRET
   ```

6. **Run Database Migrations**

   - Go to Render dashboard → Shell
   - Run: `flask db upgrade`
   - Run: `python scripts/seed_db.py` (to seed default menu items)

7. **Your backend is now live at**: `https://cater-backend.onrender.com` ✅

---

#### Frontend Deployment (Netlify):

1. **Update Frontend Environment Variables**
   Create `frontend/.env.production`:

   ```
   REACT_APP_API_URL=https://cater-backend.onrender.com
   REACT_APP_RAZORPAY_KEY=rzp_live_YOUR_KEY
   ```

2. **Build Frontend**

   ```bash
   cd frontend
   npm run build
   ```

3. **Deploy to Netlify**

   - Go to https://netlify.com
   - Drag & drop the `build` folder
   - OR connect GitHub and auto-deploy

4. **Configure Build Settings** (if using GitHub)

   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
   - Environment variables: Add `REACT_APP_API_URL` and `REACT_APP_RAZORPAY_KEY`

5. **Your frontend is now live at**: `https://yoursite.netlify.app` ✅

---

### **Option 2: Railway.app (Alternative)**

#### Backend:

1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python and builds
5. Add PostgreSQL: Click "New" → "Database" → "PostgreSQL"
6. Set environment variables (same as Render)
7. Backend deployed! ✅

#### Frontend:

Same as Netlify above, or use Vercel.

---

## 🔐 HTTPS Configuration

### ✅ Automatic HTTPS (No Manual Setup Needed!)

- **Render**: Provides automatic SSL certificates (Let's Encrypt)
- **Railway**: Provides automatic SSL certificates
- **Netlify**: Provides automatic SSL certificates
- **Vercel**: Provides automatic SSL certificates

Your websites will automatically be served over HTTPS with valid SSL certificates!

### Custom Domain HTTPS:

If you have a custom domain (e.g., `sreevegcaters.com`):

1. **Backend**:

   - In Render/Railway, go to Settings → Custom Domain
   - Add your domain: `api.sreevegcaters.com`
   - Update your DNS records (they'll provide instructions)
   - SSL certificate is auto-generated ✅

2. **Frontend**:

   - In Netlify/Vercel, go to Domain Settings
   - Add custom domain: `sreevegcaters.com`
   - Update DNS records
   - SSL certificate is auto-generated ✅

3. **Update Environment Variables**:
   - Backend: `CORS_ALLOWED_ORIGINS=https://sreevegcaters.com`
   - Frontend: `REACT_APP_API_URL=https://api.sreevegcaters.com`

---

## 🔧 Generate Secret Keys

Run these commands to generate secure keys:

```bash
# For SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"

# For JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 📦 Database Migration

After deploying, run these commands in Render Shell or Railway:

```bash
# Initialize database tables
flask db upgrade

# Seed default menu items
python scripts/seed_db.py
```

---

## 🔍 Troubleshooting

### CORS Errors:

- Make sure `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Include both `http://` and `https://` variants during testing

### Database Connection:

- Verify `DATABASE_URL` is set correctly
- For Heroku/Railway, make sure `postgres://` is changed to `postgresql://` (config.py handles this)

### Socket.IO Not Working:

- Ensure Gunicorn uses eventlet worker: `--worker-class eventlet`
- Only use 1 worker: `-w 1`

### Images Not Loading:

- Check that `/static/uploads/` directory exists
- Verify CORS allows `/static/*` paths
- Images uploaded to SQLite won't persist on Render (use PostgreSQL + file storage)

---

## 💾 File Storage (Images)

**Problem**: Uploaded images on Render/Railway are lost on restart (ephemeral filesystem).

**Solutions**:

1. **AWS S3** (Professional)

   - Create S3 bucket
   - Update upload API to save to S3
   - Return S3 URL instead of `/static/uploads/`

2. **Cloudinary** (Easiest)

   - Sign up at cloudinary.com (free tier: 25GB)
   - Install: `pip install cloudinary`
   - Update uploads.py to use Cloudinary API
   - Images are permanently stored

3. **Render Disks** (Render-specific)
   - Add persistent disk in Render dashboard
   - Mount to `/opt/render/project/src/static/uploads`
   - Costs $1/month for 1GB

For now, your default menu item images (in `frontend/public/images/`) will work fine as they're bundled with the frontend.

---

## ✅ Checklist Before Going Live

- [ ] Backend deployed and running on HTTPS
- [ ] Frontend deployed and running on HTTPS
- [ ] PostgreSQL database connected
- [ ] Database migrations run
- [ ] Default menu items seeded
- [ ] Environment variables set correctly
- [ ] CORS configured with production domains
- [ ] Razorpay LIVE keys configured (not test keys)
- [ ] Admin credentials secured
- [ ] Test order flow end-to-end
- [ ] Test payment with real Razorpay account
- [ ] Mobile responsive design checked
- [ ] All images loading correctly

---

## 🎉 Your Website is Production Ready!

Both HTTP and HTTPS will work, but modern browsers and hosting platforms enforce HTTPS by default for security. Your customers will always see the secure padlock icon 🔒 in their browser!

**Questions?** Check the deployment logs in your hosting dashboard for any errors.
