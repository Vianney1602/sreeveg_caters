# Production Deployment Guide

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.11+ (for eventlet websocket support)
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

---

## 1. Server Setup

### Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv nginx certbot python3-certbot-nginx git
```

### Create Application User

```bash
sudo useradd -m -s /bin/bash caterer
sudo usermod -aG sudo caterer
sudo su - caterer
```

---

## 2. Application Deployment

### Clone Repository

```bash
cd /home/caterer
git clone <your-repo-url> cater-app
cd cater-app/backend
```

### Setup Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn gevent gevent-websocket  # Production server
```

### Configure Environment

```bash
# Copy and edit .env
cp .env.example .env
nano .env
```

**Required .env settings for production:**

```env
# Generate strong secrets (see Security section)
SECRET_KEY=<generate-strong-random-64-chars>
JWT_SECRET_KEY=<generate-strong-random-64-chars>
JWT_ACCESS_TOKEN_EXPIRES=7200

# Admin credentials
ADMIN_USERNAME=admin@yourdomain.com
ADMIN_PASSWORD=<strong-password-here>

# CORS - YOUR PRODUCTION DOMAINS ONLY
CORS_ALLOWED_ORIGINS=https://www.yourdomain.com,https://admin.yourdomain.com

# Database (for production, consider PostgreSQL)
SQLALCHEMY_DATABASE_URI=sqlite:///database.db

# Razorpay (production keys)
RAZORPAY_KEY_ID=rzp_live_YOUR_KEY
RAZORPAY_KEY_SECRET=YOUR_SECRET

# Upload limits
MAX_CONTENT_LENGTH=5242880
ALLOWED_IMAGE_EXTENSIONS=png,jpg,jpeg,webp
```

### Initialize Database

```bash
source venv/bin/activate
python -m flask db upgrade
python scripts/seed_db.py  # Optional: seed initial data
```

---

## 3. Systemd Service Setup

Create systemd service file:

```bash
sudo nano /etc/systemd/system/caterer.service
```

**Service configuration:**

```ini
[Unit]
Description=Caterer Flask Application
After=network.target

[Service]
Type=notify
User=caterer
Group=caterer
WorkingDirectory=/home/caterer/cater-app/backend
Environment="PATH=/home/caterer/cater-app/backend/venv/bin"
ExecStart=/home/caterer/cater-app/backend/venv/bin/gunicorn \
    -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    -w 2 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/caterer/access.log \
    --error-logfile /var/log/caterer/error.log \
    wsgi:app_for_gunicorn

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Create Log Directory

```bash
sudo mkdir -p /var/log/caterer
sudo chown caterer:caterer /var/log/caterer
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable caterer
sudo systemctl start caterer
sudo systemctl status caterer
```

---

## 4. Nginx Configuration

### Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/caterer
```

**Nginx configuration:**

```nginx
# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name www.yourdomain.com admin.yourdomain.com;

    return 301 https://$server_name$request_uri;
}

# Main site
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.yourdomain.com;

    # SSL certificates (managed by certbot)
    ssl_certificate /etc/letsencrypt/live/www.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend static files (React build)
    root /home/caterer/cater-app/frontend/build;
    index index.html;

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    # Socket.IO
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_buffering off;
    }

    # Static files (uploads)
    location /static/ {
        alias /home/caterer/cater-app/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # React app (catch-all for client-side routing)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # File upload size limit
    client_max_body_size 10M;
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/caterer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Setup SSL with Let's Encrypt

```bash
sudo certbot --nginx -d www.yourdomain.com -d admin.yourdomain.com
```

---

## 5. Frontend Deployment

### Build React App

```bash
cd /home/caterer/cater-app/frontend

# Install dependencies
npm install

# Update API endpoint in .env.production
echo "REACT_APP_API_URL=https://www.yourdomain.com" > .env.production

# Build for production
npm run build
```

### Deploy Build

The Nginx config already points to `frontend/build` directory. After running `npm run build`, the static files are ready.

---

## 6. Security Hardening

### Generate Strong Secrets

```bash
# Generate random secrets
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use output for `SECRET_KEY` and `JWT_SECRET_KEY` in `.env`.

### File Permissions

```bash
cd /home/caterer/cater-app/backend
chmod 600 .env  # Restrict .env access
chmod 755 static/uploads  # Allow uploads directory
```

### Firewall

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Database Backups

```bash
# Create backup script
cat > /home/caterer/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/caterer/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /home/caterer/cater-app/backend/database.db "$BACKUP_DIR/database_$DATE.db"
# Keep only last 7 days
find $BACKUP_DIR -name "database_*.db" -mtime +7 -delete
EOF

chmod +x /home/caterer/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/caterer/backup.sh") | crontab -
```

---

## 7. Monitoring & Logs

### View Logs

```bash
# Application logs
sudo journalctl -u caterer -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application-specific logs
tail -f /var/log/caterer/error.log
```

### Health Check

```bash
curl https://www.yourdomain.com/health
```

---

## 8. Updates & Maintenance

### Update Application

```bash
cd /home/caterer/cater-app
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m flask db upgrade
sudo systemctl restart caterer

# Frontend
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

### Database Migrations

```bash
cd /home/caterer/cater-app/backend
source venv/bin/activate
python -m flask db migrate -m "Description of changes"
python -m flask db upgrade
sudo systemctl restart caterer
```

---

## 9. Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u caterer -n 50

# Check permissions
ls -la /home/caterer/cater-app/backend/database.db
ls -la /home/caterer/cater-app/backend/.env

# Test manually
cd /home/caterer/cater-app/backend
source venv/bin/activate
python -c "from app import create_app; app = create_app(); print('OK')"
```

### Nginx Errors

```bash
# Test config
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Verify backend is running
curl http://127.0.0.1:5000/health
```

### Database Locked

```bash
# SQLite can lock under high concurrency
# Consider migrating to PostgreSQL for production:
sudo apt install postgresql postgresql-contrib
# Update SQLALCHEMY_DATABASE_URI in .env
```

---

## 10. Performance Optimization

### Increase Gunicorn Workers

Edit `/etc/systemd/system/caterer.service`:

```ini
# Rule of thumb: (2 x CPU cores) + 1
ExecStart=... -w 5 ...  # For 2-core server
```

### Enable Gzip Compression

Add to nginx config:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
gzip_min_length 1000;
```

### Database Optimization

```bash
# For SQLite
sqlite3 database.db 'VACUUM;'

# Consider PostgreSQL for >1000 users
```

---

## Production Checklist

- [ ] Strong `SECRET_KEY` and `JWT_SECRET_KEY` in `.env`
- [ ] `CORS_ALLOWED_ORIGINS` set to production domains only (no localhost)
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Firewall configured (UFW or iptables)
- [ ] Database backups automated
- [ ] `.env` file permissions set to 600
- [ ] Admin password changed from default
- [ ] Razorpay production keys configured
- [ ] Health check endpoint responds OK
- [ ] Logs rotating properly (logrotate)
- [ ] Monitoring setup (optional: UptimeRobot, Datadog)
- [ ] Frontend environment variables point to production API

---

## Support & Resources

- Flask docs: https://flask.palletsprojects.com/
- Gunicorn docs: https://docs.gunicorn.org/
- Nginx docs: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/
- Razorpay docs: https://razorpay.com/docs/

---

**Last Updated**: December 2025
