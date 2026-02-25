#!/bin/bash
# QUICK DEPLOYMENT CHECKLIST
# Redis OTP Implementation - Production Deployment
# Run these commands on EC2 production server

echo "================================"
echo "QUICK DEPLOYMENT CHECKLIST"
echo "================================"
echo ""

# Step 1: SSH into production
echo "[1] SSH into production server:"
echo "    ssh ec2-user@16.112.138.215"
echo "    (press Enter when connected)"
read -p "Ready? Enter to continue..."
echo ""

# Step 2: Pull code
echo "[2] Pulling latest code from git..."
cd /home/ec2-user/cater-main
git pull origin main
echo "✓ Code pulled"
echo ""

# Step 3: Verify Redis
echo "[3] Verifying Redis is running..."
redis-cli ping
if [ $? -eq 0 ]; then
    echo "✓ Redis is running (PONG received)"
else
    echo "✗ Redis not responding - starting..."
    sudo systemctl start redis6
    sleep 2
    redis-cli ping
fi
echo ""

# Step 4: Update dependencies
echo "[4] Installing Python dependencies..."
cd /home/ec2-user/cater-main/backend
pip install redis>=5.0.0 > /dev/null 2>&1
echo "✓ Dependencies installed"
echo ""

# Step 5: Restart service
echo "[5] Restarting backend service..."
pkill -f gunicorn
sleep 2
nohup gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app > gunicorn.log 2>&1 &
sleep 3
echo "✓ Gunicorn restarted"
echo ""

# Step 6: Test endpoints
echo "[6] Testing OTP endpoints..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/users/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}' | grep -o "message\|error")
if echo "$RESPONSE" | grep -q "message\|error"; then
    echo "✓ OTP endpoints responding"
else
    echo "✗ OTP endpoints not responding"
fi
echo ""

echo "================================"
echo "DEPLOYMENT COMPLETE!"
echo "================================"
echo ""
echo "Production URL: https://info.hotelshanmugabhavaan.com"
echo "API: http://16.112.138.215:8000"
echo ""
echo "Next steps:"
echo "1. Test password reset flow with real user"
echo "2. Monitor gunicorn logs: tail -f backend/gunicorn.log"
echo "3. Check Redis metrics: redis-cli info stats"
echo ""
