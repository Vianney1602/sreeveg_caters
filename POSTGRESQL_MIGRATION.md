# SQLite → PostgreSQL Migration Guide

## ✅ Will PostgreSQL Work for Your Data?

**YES! 100%** PostgreSQL is perfect for:

- ✅ Customer details
- ✅ Orders and order items
- ✅ Menu items
- ✅ All existing data

PostgreSQL is actually BETTER than SQLite for:

- Multiple concurrent orders (SQLite gets locked with simultaneous writes)
- Data reliability and backup
- Production deployment
- Scaling to thousands of orders

---

## 📋 Step-by-Step Migration

### Step 1: Install PostgreSQL

#### Windows:

1. Download from: https://www.postgresql.org/download/windows/
2. Run the installer
3. Remember your **password** (set during installation) - you'll need it!
4. Accept default settings
5. After installation, PostgreSQL will be running

#### macOS:

```bash
brew install postgresql@15
```

#### Linux (Ubuntu/Debian):

```bash
sudo apt-get install postgresql postgresql-contrib
```

---

### Step 2: Create PostgreSQL Database

#### Option A: Using SQL Shell (Easiest)

1. Open "SQL Shell" application (installed with PostgreSQL)
2. Press Enter for all defaults until you see: `postgres=#`
3. Paste and run:

```sql
CREATE DATABASE cater_db;
```

4. Type `\q` and press Enter to exit

#### Option B: Using pgAdmin GUI

1. Open "pgAdmin 4" (installed with PostgreSQL)
2. Right-click "Databases" → "Create" → "Database"
3. Enter name: `cater_db`
4. Click "Save"

---

### Step 3: Update Your Backend Configuration

Open `backend/.env` and add/update:

```bash
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/cater_db
```

Replace `YOUR_PASSWORD` with the password you entered during PostgreSQL installation.

**Example:**

```bash
DATABASE_URL=postgresql://postgres:MyPassword123@localhost:5432/cater_db
```

---

### Step 4: Run Migration Script

```bash
cd H:\cater-main\backend
python scripts/migrate_sqlite_to_pg.py
```

**What the script does:**

1. Reads all data from SQLite (database.db)
2. Creates PostgreSQL tables
3. Imports all customers, orders, menu items, etc.
4. Verifies everything is correct

**Expected output:**

```
======================================================================
DATABASE MIGRATION: SQLite → PostgreSQL
======================================================================

✅ DATABASE_URL is set!

📖 Reading data from SQLite...
   Customers: 5
   Orders: 12
   Order Items: 24
   Menu Items: 9
   Event Types: 2
   Stats: 3
   Inquiries: 8

✍️  Writing to PostgreSQL...
   ✅ Migrated 5 customers
   ✅ Migrated 9 menu items
   ✅ Migrated 2 event types
   ✅ Migrated 12 orders
   ✅ Migrated 24 order items
   ✅ Migrated 3 monthly stats
   ✅ Migrated 8 inquiries

======================================================================
✅ MIGRATION COMPLETE!
======================================================================
```

---

### Step 5: Test Your Website

1. **Stop the backend server** (if running)
2. **Start the backend server again:**
   ```bash
   cd backend
   python app.py
   ```
3. **Test in your browser:**
   - Go to http://localhost:3000
   - Check that menu items appear ✅
   - Place a test order ✅
   - Admin dashboard shows your old orders ✅

---

## ✅ Verification

After migration, verify all data is present:

```bash
# Check customer count
python -c "from app import create_app; from models import Customer; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Customers: {Customer.query.count()}')"

# Check order count
python -c "from app import create_app; from models import Order; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Orders: {Order.query.count()}')"

# Check menu items
python -c "from app import create_app; from models import MenuItem; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Menu items: {MenuItem.query.count()}')"
```

---

## 🆘 Troubleshooting

### Error: "password authentication failed"

**Solution:** Wrong password in DATABASE_URL

- Check your PostgreSQL password again
- Update DATABASE_URL in .env
- Re-run migration script

### Error: "psycopg2 not found"

**Solution:** Install missing package

```bash
pip install psycopg2-binary
```

### Error: "database does not exist"

**Solution:** You haven't created cater_db

- Follow Step 2 above
- Create the database first
- Then run migration

### Orders/customers not showing after migration

**Solution:** Restart backend server

```bash
# Stop: Ctrl+C
# Start again:
python app.py
```

---

## 🔄 Backup Your SQLite (Before Deleting)

Before deleting `database.db`, backup it:

```bash
copy backend\database.db backend\database.db.backup
```

Keep this backup for 1-2 weeks to ensure migration was successful.

---

## 🎯 What Changes After Migration?

### For You (Admin):

- Nothing! Everything works the same
- But now you have:
  - Better performance with multiple orders
  - More reliable data storage
  - Easy backups via PostgreSQL

### For Customers:

- Nothing! Their experience is identical
- Faster responses with concurrent orders
- More stable system

### For Deployment:

- ✅ Can now deploy to Render/Railway/Heroku
- ✅ These platforms provide free PostgreSQL
- ✅ Your website goes live with HTTPS!

---

## 📊 Database Comparison

| Feature           | SQLite        | PostgreSQL            |
| ----------------- | ------------- | --------------------- |
| Concurrent orders | ❌ Locks      | ✅ Works fine         |
| Data reliability  | ⚠️ File-based | ✅ Robust             |
| Backup            | 📁 Copy file  | ✅ Easy               |
| Scaling           | ❌ Slow       | ✅ Fast               |
| Production ready  | ❌ No         | ✅ Yes                |
| Deployment        | ❌ Hard       | ✅ Easy               |
| Cost              | Free          | Free (Render/Railway) |

---

## ✨ Next Steps

1. ✅ Backup SQLite: `copy database.db database.db.backup`
2. ✅ Install PostgreSQL (if not done)
3. ✅ Create `cater_db` database
4. ✅ Update DATABASE_URL in .env
5. ✅ Run migration script
6. ✅ Test everything
7. ✅ Ready to deploy!

---

## 🎉 You're All Set!

Your website is now running on PostgreSQL with all your data safely migrated. You can confidently deploy to production knowing your data is secure and scalable!

**Questions?** Check the troubleshooting section above or review your backend logs.
