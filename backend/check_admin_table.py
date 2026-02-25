import os
import sqlalchemy as sa

url = os.environ.get('DATABASE_URL')
if not url:
    print('DATABASE_URL not set')
    raise SystemExit(1)

engine = sa.create_engine(url)
with engine.connect() as conn:
    r = conn.execute("SELECT to_regclass('public.admin_settings')").fetchone()
    print('to_regclass:', r)
    rows = conn.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='admin_settings'").fetchone()
    print('table_count:', rows[0])
    if rows[0] > 0:
        print('admin_settings exists')
    else:
        print('admin_settings does NOT exist')
