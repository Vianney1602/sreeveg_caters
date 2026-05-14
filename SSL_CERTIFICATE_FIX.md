# SSL Certificate Configuration Fix

## Problem
Frontend (HTTPS) cannot connect to Backend (needs HTTPS or proper proxy)
- Console Error: `ERR_CERT_DATE_INVALID` 
- Backend currently missing valid SSL certificate on port 8000
- Mixed-content policy blocks HTTP calls from HTTPS pages

## Solution: Install Free SSL Certificate with Certbot

### Step 1: SSH into EC2 Instance
```bash
ssh -i your-key.pem ec2-user@ec2-instance-ip
```

### Step 2: Install Certbot (Let's Encrypt)
```bash
sudo yum update -y
sudo yum install certbot python3-certbot-nginx -y
```

### Step 3: Get Certificate for Your Domain
```bash
sudo certbot certonly --standalone \
  -d hotelshanmugabhavaan.com \
  -d www.hotelshanmugabhavaan.com \
  --agree-tos \
  --non-interactive \
  --email hotelshanmugabhavaan@gmail.com
```

### Step 4: Copy Certificates to Backend Directory
```bash
sudo cp /etc/letsencrypt/live/hotelshanmugabhavaan.com/fullchain.pem \
  /path/to/backend/cert.pem

sudo cp /etc/letsencrypt/live/hotelshanmugabhavaan.com/privkey.pem \
  /path/to/backend/key.pem

sudo chown ec2-user:ec2-user /path/to/backend/cert.pem
sudo chown ec2-user:ec2-user /path/to/backend/key.pem
```

### Step 5: Restart Backend Service
```bash
# If using systemd
sudo systemctl restart gunicorn

# Or manually restart
cd /path/to/backend
pkill -f "python app.py"
python app.py &
```

### Step 6: Update Frontend .env.production
```
REACT_APP_API_BASE_URL=https://hotelshanmugabhavaan.com:8000
REACT_APP_SOCKET_URL=https://hotelshanmugabhavaan.com:8000
```

### Step 7: Auto-Renewal (Cron Job)
```bash
# Let Certbot handle auto-renewal
sudo systemctl start certbot-renew.timer
sudo systemctl enable certbot-renew.timer

# Or manual renewal every 2 months
0 3 1 */2 * sudo certbot renew --quiet
```

## Alternative: AWS ACM + Application Load Balancer
If running on AWS, use:
1. AWS Certificate Manager (ACM) for free SSL
2. Application Load Balancer (ALB) to terminate SSL
3. ALB forwards to EC2 on HTTP:8000

This is more secure and recommended for production.

## Fortinet SSL Inspection Certificate
If the browser is showing a Fortinet interception certificate, export the trusted Fortinet root certificate from Windows and keep it updated automatically.

### Export + automate on Windows
```powershell
Set-Location d:\sreeveg_caters
PowerShell -ExecutionPolicy Bypass -File .\scripts\export_fortinet_certificate.ps1 -RegisterScheduledTask
```

### Output
- Exports the latest Fortinet certificate to `scripts\fortinet-root.cer`
- Registers a weekly scheduled task for refresh
- Uses only the local Windows certificate store; it does not change production deployment

### Production safety
- `frontend/src/setupProxy.js` is used only by the CRA dev server
- Production builds use the backend URL from environment variables, so localhost proxy changes do not affect the live site

## Testing SSL
```bash
# Test certificate
curl -v https://hotelshanmugabhavaan.com:8000/health

# Should show valid certificate (not ERR_CERT_DATE_INVALID)
```

## Current Status
- Frontend .env.production updated: ✅
- Backend needs SSL certificate: ⏳
- Will fix menu loading and login after SSL is configured
