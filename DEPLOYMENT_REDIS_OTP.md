## Production Deployment Guide - Redis OTP Fix

### Overview
This guide deploys the Redis OTP implementation fix to production. The fix resolves OTP verification failures that occurred in multi-worker gunicorn deployments.

### Pre-Deployment Checklist
- [ ] Code committed to git: `bed9ca4 Fix OTP verification failures with Redis implementation`
- [ ] Code pushed to origin/main
- [ ] EC2 instance running (16.112.138.215)
- [ ] SSH access available
- [ ] Redis running on EC2
- [ ] Gunicorn configured on EC2

### Production Environment
- **Server**: AWS EC2 - Amazon Linux 2023
- **IP**: 16.112.138.215
- **Port**: 8000
- **URL**: https://info.hotelshanmugabhavaan.com
- **Process Manager**: Gunicorn (4 workers)
- **Cache**: Redis6

### Deployment Steps

#### Option 1: Automated Deployment (Recommended)

1. **Copy deployment script to EC2:**
   ```bash
   scp deploy_production.sh ec2-user@16.112.138.215:/home/ec2-user/
   ```

2. **SSH into EC2 and execute:**
   ```bash
   ssh ec2-user@16.112.138.215
   chmod +x deploy_production.sh
   ./deploy_production.sh
   ```

3. **Monitor output** - Script will:
   - Pull latest code from git
   - Verify Redis is running
   - Update Python dependencies
   - Restart gunicorn service
   - Test OTP endpoints

---

#### Option 2: Manual Deployment Steps

1. **SSH into EC2:**
   ```bash
   ssh ec2-user@16.112.138.215
   ```

2. **Navigate to project directory:**
   ```bash
   cd /home/ec2-user/cater-main
   ```

3. **Pull latest code:**
   ```bash
   git pull origin main
   ```
   Expected: `bed9ca4 Fix OTP verification failures with Redis implementation`

4. **Verify Redis is running:**
   ```bash
   redis-cli ping
   ```
   Expected output: `PONG`
   
   If not running, start it:
   ```bash
   sudo systemctl start redis6
   ```

5. **Update dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
   Should install/update: `redis>=5.0.0`

6. **Stop old gunicorn processes:**
   ```bash
   pkill -f gunicorn
   ```

7. **Start new gunicorn service:**
   ```bash
   cd /home/ec2-user/cater-main/backend
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app &
   ```
   Or if using systemd service:
   ```bash
   sudo systemctl restart cater-backend
   ```

8. **Verify deployment:**
   ```bash
   # Test basic connectivity
   curl http://localhost:8000/
   
   # Test OTP forgot-password endpoint
   curl -X POST http://localhost:8000/api/users/forgot-password \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com"}'
   ```

---

### Post-Deployment Verification

#### 1. Check Redis Connection
```bash
redis-cli ping
# Expected: PONG

redis-cli info server | grep redis_version
# Verify Redis6 is installed
```

#### 2. Check Backend Service
```bash
# Verify gunicorn is running on port 8000
netstat -tulpn | grep 8000
# Should see: 0.0.0.0:8000 LISTEN

# Check gunicorn logs
tail -f backend/gunicorn.log
# Should see: "[INFO] Application startup complete"
```

#### 3. Test OTP Flow Manually

Create test user:
```bash
curl -X POST http://16.112.138.215:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123!",
    "phone": "1234567890"
  }'
```

Request OTP:
```bash
curl -X POST http://16.112.138.215:8000/api/users/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
# Expected: {"message":"OTP generated successfully..."}
```

Get OTP from Redis:
```bash
redis-cli get "otp:test@example.com"
# Should return 6-digit OTP code
```

Verify OTP (replace with actual OTP):
```bash
curl -X POST http://16.112.138.215:8000/api/users/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","otp":"123456"}'
# Expected: {"message":"OTP verified successfully"} or error if wrong OTP
```

Reset Password:
```bash
curl -X POST http://16.112.138.215:8000/api/users/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "otp":"123456",
    "new_password":"NewPassword456!"
  }'
# Expected: {"message":"Password reset successfully"}
```

#### 4. Monitor Redis Memory
```bash
# Check Redis memory usage
redis-cli info memory | grep used_memory_human

# Check if OTP keys are being stored
redis-cli keys "otp:*" | wc -l
```

---

### Rollback Plan (if needed)

If deployment fails, rollback to previous version:

```bash
# Revert last commit
git revert HEAD

# Or reset to previous working version
git reset --hard HEAD~1

# Restart services
pkill -f gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app &
```

---

### Key Files Changed

| File | Changes |
|------|---------|
| `backend/api/users.py` | Added Redis integration for OTP storage |
| `backend/requirements.txt` | Added `redis>=5.0.0` dependency |
| `backend/app.py` | No changes (already configured) |

**Lines of code changed**: ~118 insertions, 34 deletions

---

### Troubleshooting

**Problem**: "redis connection refused"
- **Solution**: Ensure Redis is running: `redis-cli ping`

**Problem**: "OTP not found or expired"
- **Solution**: Check Redis is working and OTP TTL: `redis-cli ttl "otp:email@domain.com"`

**Problem**: Gunicorn won't start
- **Solution**: Check logs: `cat backend/gunicorn.log`, ensure port 8000 is free

**Problem**: ModuleNotFoundError: No module named 'redis'
- **Solution**: Install dependencies: `pip install -r backend/requirements.txt`

---

### Monitoring (Ongoing)

Monitor these metrics post-deployment:

```bash
# 1. Application Health
curl -s http://16.112.138.215:8000/ | grep -q "Flask" && echo "✓ Healthy" || echo "✗ Unhealthy"

# 2. Redis Connection
redis-cli ping

# 3. OTP Success Rate
# Track in application logs - should see [INFO] messages for successful OTP operations

# 4. Error Tracking
tail -f backend/gunicorn.log | grep ERROR
```

---

### Completion Checklist

- [ ] Code deployed to production
- [ ] Redis verified running
- [ ] Gunicorn restarted
- [ ] OTP endpoints tested and working
- [ ] Test user able to request OTP
- [ ] Test user able to verify OTP
- [ ] Test user able to reset password
- [ ] No errors in gunicorn logs
- [ ] Redis keys properly stored and expired

---

**Deployed Version**: `bed9ca4`
**Deployment Date**: 2026-02-25
**Status**: Ready for Production
