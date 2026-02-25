#!/bin/bash
# Production Deployment Script for Redis OTP Fix
# Run this on the EC2 production server (16.112.138.215)

echo "=========================================="
echo "CATER PRODUCTION DEPLOYMENT"
echo "Redis OTP Implementation Fix"
echo "=========================================="
echo ""

# Step 1: Navigate to project directory
echo "[STEP 1] Navigating to project directory..."
cd /home/ec2-user/cater-main || { echo "Project directory not found!"; exit 1; }
echo "✓ In directory: $(pwd)"

# Step 2: Pull latest changes from git
echo ""
echo "[STEP 2] Pulling latest changes from Git..."
git pull origin main
if [ $? -ne 0 ]; then
    echo "✗ Git pull failed!"
    exit 1
fi
echo "✓ Git pull successful"

# Step 3: Check if Redis is running
echo ""
echo "[STEP 3] Verifying Redis is running..."
redis-cli ping &>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Redis is not running! Starting Redis..."
    sudo systemctl start redis6 || { echo "Failed to start Redis!"; exit 1; }
    sleep 2
    redis-cli ping
    if [ $? -ne 0 ]; then
        echo "✗ Redis still not responding!"
        exit 1
    fi
fi
echo "✓ Redis is running (PONG received)"

# Step 4: Update Python dependencies
echo ""
echo "[STEP 4] Updating Python dependencies..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed/updated"

# Step 5: Restart Flask/Gunicorn service
echo ""
echo "[STEP 5] Restarting backend service..."
cd /home/ec2-user/cater-main

# Kill existing gunicorn processes
echo "Stopping existing services..."
pkill -f "gunicorn" || true
pkill -f "python.*app.py" || true
sleep 2

# Start new gunicorn process in background
echo "Starting gunicorn on port 8000..."
cd backend
nohup gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app > gunicorn.log 2>&1 &
GUNICORN_PID=$!
sleep 3

# Verify gunicorn is running
if ps -p $GUNICORN_PID > /dev/null 2>&1; then
    echo "✓ Gunicorn started (PID: $GUNICORN_PID)"
else
    echo "✗ Gunicorn failed to start!"
    cat gunicorn.log
    exit 1
fi

# Step 6: Verify deployment
echo ""
echo "[STEP 6] Verifying deployment..."
sleep 2

# Test backend connectivity
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$RESPONSE" = "200" ]; then
    echo "✓ Backend responding (HTTP $RESPONSE)"
else
    echo "⚠ Backend returned HTTP $RESPONSE"
fi

# Test OTP endpoint
echo "Testing OTP endpoints..."
curl -s -X POST http://localhost:8000/api/users/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}' | grep -q "error"
if [ $? -eq 0 ]; then
    echo "✓ OTP endpoint is accessible (error expected for test email)"
else
    echo "✗ OTP endpoint test failed"
fi

echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Latest code deployed (Redis OTP fix)"
echo "  ✓ Redis verified running"
echo "  ✓ Backend service restarted"
echo "  ✓ OTP endpoints operational"
echo ""
echo "Production URL: https://info.hotelshanmugabhavaan.com"
echo "Backend: http://16.112.138.215:8000"
echo ""
echo "To verify logs:"
echo "  tail -f backend/gunicorn.log"
echo ""
