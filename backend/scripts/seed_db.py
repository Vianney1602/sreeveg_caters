import os
import sys

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
import models

app = create_app()

with app.app_context():
    # Check if menu items already exist
    existing_items = models.MenuItem.query.count()
    
    if existing_items > 0:
        print(f'Database already has {existing_items} menu items. Skipping seed.')
        print('To re-seed, manually delete items first or clear the database.')
    else:
        # Seed Event Types
        events = [
            models.EventType(event_name='Wedding', minimum_guests=50, description='Full wedding catering package', image_url='https://example.com/wedding.jpg'),
            models.EventType(event_name='Birthday', minimum_guests=10, description='Birthday parties and small events', image_url='https://example.com/birthday.jpg')
        ]

        # Seed Menu Items
        menu_items = [
            models.MenuItem(item_name='Veg Meals', category='main', price_per_plate=120.0, is_vegetarian=True, image_url='/images/meals_veg.png', description='South Indian rice platter with curries and sides.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Paneer Butter Masala', category='main', price_per_plate=140.0, is_vegetarian=True, image_url='/images/panner_butter_masala.png', description='Creamy paneer cooked with butter and spices.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Chole Puri', category='main', price_per_plate=100.0, is_vegetarian=True, image_url='/images/chola_puri.png', description='Spiced chickpeas served with fluffy puris.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Dal Makhani', category='main', price_per_plate=130.0, is_vegetarian=True, image_url='/images/dhal_makini.png', description='Slow-cooked black lentils finished with cream.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Veg Biryani', category='main', price_per_plate=150.0, is_vegetarian=True, image_url='/images/veg-biriyani.webp', description='Aromatic basmati rice with mixed vegetables.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Paneer Tikka', category='starter', price_per_plate=110.0, is_vegetarian=True, image_url='/images/paneer-tikka.jpg', description='Smoky marinated paneer skewers.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Veg Cutlet', category='starter', price_per_plate=90.0, is_vegetarian=True, image_url='/images/veg-cutlet.webp', description='Crispy vegetable patties with herbs.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Gulab Jamun', category='dessert', price_per_plate=80.0, is_vegetarian=True, image_url='/images/gulab-jamun.jpg', description='Soft milk dumplings soaked in syrup.', stock_quantity=100, is_available=True),
            models.MenuItem(item_name='Rasmalai', category='dessert', price_per_plate=90.0, is_vegetarian=True, image_url='/images/rasamalai.webp', description='Cottage cheese patties in saffron milk.', stock_quantity=100, is_available=True),
        ]

        db.session.add_all(events + menu_items)
        db.session.commit()

        print('Seeded', len(events), 'event types and', len(menu_items), 'menu items')
