import os
from app import create_app, db
from models import MenuItem

# New menu dataset derived from provided image menus
MENU_DATA = [
    # Morning Tiffin Menu
    {"name": "Kesari", "price": 30, "category": "Morning Tiffin Menu"},
    {"name": "Idly (2)", "price": 30, "category": "Morning Tiffin Menu"},
    {"name": "Vada", "price": 15, "category": "Morning Tiffin Menu"},
    {"name": "Masal Vada", "price": 15, "category": "Morning Tiffin Menu"},
    {"name": "Pongal", "price": 50, "category": "Morning Tiffin Menu"},
    {"name": "Poori Masala (2)", "price": 50, "category": "Morning Tiffin Menu"},
    {"name": "Vegetable Kitchedi", "price": 50, "category": "Morning Tiffin Menu"},
    {"name": "Kothuma Rava Uppuma", "price": 60, "category": "Morning Tiffin Menu"},
    {"name": "Dosa", "price": 40, "category": "Morning Tiffin Menu"},
    {"name": "Masal Dosa", "price": 60, "category": "Morning Tiffin Menu"},
    {"name": "Podi Dosa", "price": 60, "category": "Morning Tiffin Menu"},
    {"name": "Ghee Dosa", "price": 60, "category": "Morning Tiffin Menu"},
    {"name": "Butter Dosa", "price": 60, "category": "Morning Tiffin Menu"},
    {"name": "Rava Dosa (1 pc)", "price": 60, "category": "Morning Tiffin Menu"},

    # Lunch Menu - Regular Meals (single plate includes items from image)
    {"name": "Regular Meals", "price": 140, "category": "Lunch Menu - Regular Meals", "description": "Includes sweet, rice, sambar, rasam, vathakuzhambu, kootu, poriyal, curd, appalam, pickle"},

    # Lunch Menu - Mini Meals
    {"name": "Mini Meals", "price": 150, "category": "Lunch Menu - Mini Meals", "description": "Includes sweet, chapathy, kuruma, rice, sambar, rasam, kootu, vathakuzhambu, poriyal, curd, appalam, pickle"},

    # Lunch Menu - Variety Rice (each plate)
    {"name": "Puliyodharai", "price": 70, "category": "Lunch Menu - Variety Rice"},
    {"name": "Coconut Rice", "price": 70, "category": "Lunch Menu - Variety Rice"},
    {"name": "Lemon Rice", "price": 70, "category": "Lunch Menu - Variety Rice"},
    {"name": "Vegetable Pulav", "price": 70, "category": "Lunch Menu - Variety Rice"},
    {"name": "Mint Rice", "price": 70, "category": "Lunch Menu - Variety Rice"},
    {"name": "Tomato Rice", "price": 70, "category": "Lunch Menu - Variety Rice"},

    # Dinner Menu
    {"name": "Kesari", "price": 30, "category": "Dinner Menu"},
    {"name": "Idly (2)", "price": 30, "category": "Dinner Menu"},
    {"name": "Vada", "price": 15, "category": "Dinner Menu"},
    {"name": "Dosa", "price": 40, "category": "Dinner Menu"},
    {"name": "Masal Dosa", "price": 60, "category": "Dinner Menu"},
    {"name": "Podi Dosa", "price": 60, "category": "Dinner Menu"},
    {"name": "Ghee Dosa", "price": 60, "category": "Dinner Menu"},
    {"name": "Butter Dosa", "price": 60, "category": "Dinner Menu"},
    {"name": "Rava Dosa (1 pc)", "price": 60, "category": "Dinner Menu"},
    {"name": "14 Mini Idly", "price": 60, "category": "Dinner Menu"},
    {"name": "Sambar Mini Idly", "price": 60, "category": "Dinner Menu"},
    {"name": "Fried Mini Idly", "price": 60, "category": "Dinner Menu"},
    {"name": "Adai Aviyal", "price": 60, "category": "Dinner Menu"},
    {"name": "Chapathy (2) Kuruma", "price": 50, "category": "Dinner Menu"},
    {"name": "Chola Poori (1) Chenna", "price": 75, "category": "Dinner Menu"},
    {"name": "Parotta (2) Kuruma", "price": 50, "category": "Dinner Menu"},
    {"name": "Onion Uthappam", "price": 40, "category": "Dinner Menu"},
    {"name": "Vegetable Uthappam", "price": 40, "category": "Dinner Menu"},
    {"name": "Set Dosa (2)", "price": 40, "category": "Dinner Menu"},
    {"name": "Pidi Kozhakattai (2)", "price": 30, "category": "Dinner Menu"},
    {"name": "Arisi Uppuma", "price": 50, "category": "Dinner Menu"},
]


def reset_menu():
    app = create_app()
    with app.app_context():
        # Clear all existing menu items
        deleted = MenuItem.query.delete()
        db.session.commit()
        print(f"Deleted {deleted} existing menu items")

        # Insert new items
        for entry in MENU_DATA:
            item = MenuItem(
                item_name=entry["name"],
                category=entry["category"],
                price_per_plate=entry["price"],
                is_vegetarian=True,
                description=entry.get("description", ""),
                is_available=True,
            )
            db.session.add(item)
        db.session.commit()
        print(f"Inserted {len(MENU_DATA)} menu items")


if __name__ == "__main__":
    reset_menu()
