# PostgreSQL Migration Checklist

## Before Migration

- [ ] Backup your SQLite database: `copy backend\database.db backend\database.db.backup`
- [ ] PostgreSQL installer downloaded from postgresql.org
- [ ] Ready to run migration script

## Installation & Setup

- [ ] PostgreSQL installed (Windows/Mac/Linux)
- [ ] PostgreSQL password saved (from installation)
- [ ] SQL Shell or pgAdmin opened
- [ ] Database created: `CREATE DATABASE cater_db;`

## Configuration

- [ ] `backend/.env` file updated with DATABASE_URL
- [ ] DATABASE_URL format verified:
  ```
  postgresql://postgres:YOUR_PASSWORD@localhost:5432/cater_db
  ```
- [ ] PASSWORD replaced with actual PostgreSQL password

## Migration Execution

- [ ] Navigate to: `cd backend`
- [ ] Run script: `python scripts/migrate_sqlite_to_pg.py`
- [ ] Script completed without errors
- [ ] All data counts displayed correctly

## Post-Migration Testing

- [ ] Backend server restarted
- [ ] Frontend loads without errors: http://localhost:3000
- [ ] Menu items display correctly
- [ ] Customer data visible in admin dashboard
- [ ] Orders show in admin dashboard
- [ ] Can place new order (tests PostgreSQL writes)
- [ ] New order appears in database

## Verification Commands

```bash
# Check customers
python -c "from app import create_app; from models import Customer; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Customers: {Customer.query.count()}')"

# Check orders
python -c "from app import create_app; from models import Order; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Orders: {Order.query.count()}')"

# Check menu items
python -c "from app import create_app; from models import MenuItem; app = create_app(); ctx = app.app_context(); ctx.push(); print(f'Menu items: {MenuItem.query.count()}')"
```

## Cleanup

- [ ] Verify all data is in PostgreSQL (no missing customers/orders)
- [ ] Keep `database.db.backup` for 2 weeks minimum
- [ ] (Optional) Delete `database.db` after confirming success

## Deployment Ready

- [ ] PostgreSQL migration complete
- [ ] All data verified
- [ ] Website tested and working
- [ ] Ready to deploy to Render/Railway

## Common Issues & Solutions

### "password authentication failed"

- Check PostgreSQL password in .env
- Verify DATABASE_URL format
- Passwords are case-sensitive!

### "psycopg2 not found"

```bash
pip install psycopg2-binary
```

### "database does not exist"

- Create cater_db in pgAdmin or SQL Shell
- Run: `CREATE DATABASE cater_db;`

### Data not showing after migration

- Restart backend server
- Check that app.py uses create_app()
- Verify DATABASE_URL is set

## Success Indicators

✅ All records migrated (customers, orders, menu items)
✅ Admin dashboard shows existing orders
✅ New orders can be placed and stored
✅ No error messages in backend logs
✅ Frontend loads without CORS errors

---

**Need help?** See POSTGRESQL_MIGRATION.md for detailed instructions.
