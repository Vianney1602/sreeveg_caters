import sys, os
sys.path.insert(0, '.')
from app import app
from extensions import db
from models import MenuItem

with app.app_context():
    item = MenuItem.query.get(46)
    if item:
        print(f"Before: id={item.item_id}, name={item.item_name}, image={item.image_url}")
        item.image_url = "https://s3.ap-south-2.amazonaws.com/hotelshanmugabhavaan.com/menu+items/paneer-tikka_c10216b4.jpg"
        db.session.commit()
        print(f"After:  id={item.item_id}, name={item.item_name}, image={item.image_url}")
    else:
        print("Item 46 not found")
