import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import socketService from "./services/socketService";
import MenuCard from "./MenuCard";
import "./menu.css";

// Keep a consistent priority so shared dishes prefer their first slot (tiffin wins over dinner)
const CATEGORY_PRIORITY = [
  "Morning Tiffin Menu",
  "Lunch Menu",
  "Dinner Menu"
];

const normalizeName = (name = "") => name.trim().toLowerCase();
const categoryRank = (type = "") => {
  const idx = CATEGORY_PRIORITY.indexOf(type);
  return idx === -1 ? CATEGORY_PRIORITY.length : idx;
};

const DINNER_DUP_NAMES = new Set([
  "kesari",
  "idly(2)",
  "idly (2)",
  "vada",
  "masal dosa",
  "masala dosa",
  "podi dosa",
  "ghee dosa",
  "butter dosa",
  "rava dosa"
].map(normalizeName));

const getLinkedCategories = (name = "", type = "") => {
  const norm = normalizeName(name);
  const links = [];
  if (type === "Morning Tiffin Menu" && DINNER_DUP_NAMES.has(norm)) links.push("Dinner Menu");
  if (type === "Dinner Menu" && DINNER_DUP_NAMES.has(norm)) links.push("Morning Tiffin Menu");
  return links;
};

const dedupeMenuItems = (items = []) => {
  // Items now have categories as arrays in the database
  // No need for complex deduplication - just return the items
  return items.map(item => ({
    ...item,
    sourceIds: [item.id]
  }));
};

export default function MenuPage({ goBack, goToCart, cart = {}, updateQty, addToCart }) {
  const [menuData, setMenuData] = useState([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");

  // Helper function to resolve image URLs
  const resolveImageUrl = (url) => {
    if (!url) return '/images/default-food.png';
    const trimmed = String(url).trim();

    // If it's a data URL or absolute URL, return as-is
    if (/^(data:|https?:)/i.test(trimmed)) return trimmed;

    // Get backend base URL - use axios defaults or environment
    const backendBase = (axios.defaults && axios.defaults.baseURL) ||
      process.env.REACT_APP_API_URL ||
      'http://127.0.0.1:5000';

    const toBackendUrl = (path) => {
      const clean = path.replace(/^\/+/, '');
      return `${backendBase}/${clean}`;
    };

    // If it starts with /static, static, /uploads, or uploads, treat as backend asset
    if (
      trimmed.startsWith('/static') ||
      trimmed.startsWith('static') ||
      trimmed.startsWith('/uploads') ||
      trimmed.startsWith('uploads') ||
      trimmed.includes('/static/') ||
      trimmed.includes('/uploads/')
    ) {
      return toBackendUrl(trimmed);
    }

    // If it starts with /api, it's a backend URL
    if (trimmed.startsWith('/api')) {
      const cleanPath = trimmed.replace(/^\/+/, '/');
      return `${backendBase}${cleanPath}`;
    }

    // If it starts with /images, it's a frontend public image
    if (trimmed.startsWith('/images')) {
      const base = process.env.PUBLIC_URL || '';
      return `${base}${trimmed}`;
    }

    // Fallback: assume backend-relative path
    return toBackendUrl(trimmed);
  };

  // Fetch menu items from API on mount
  useEffect(() => {
    axios.get('/api/menu')
      .then((res) => {
        const items = res.data.map(item => {
          const categories = Array.isArray(item.category) ? item.category : [item.category];
          return {
            id: item.item_id,
            name: item.item_name,
            type: categories[0], // Use first category as primary type for sorting
            categories: categories,
            description: item.description || '',
            price: item.price_per_plate,
            image: resolveImageUrl(item.image_url),
            stock: item.stock_quantity !== null ? item.stock_quantity : 100,
            available: item.is_available
          };
        });
        setMenuData(items);
      })
      .catch(() => {});
  }, []);

  // Listen for real-time menu changes and inventory updates
  useEffect(() => {
    // Handle inventory changes (stock updates)
    const onInventoryChange = (data) => {
      setMenuData(prevMenu =>
        prevMenu.map(item =>
          item.id === data.item_id
            ? {
                ...item,
                stock: data.new_stock,
                available: data.is_available
              }
            : item
        )
      );

      // Show notification for low stock
      if (data.low_stock && Notification.permission === 'granted') {
        new Notification('Low Stock Alert', {
          body: `${data.item_name} is running low (${data.new_stock} remaining)`,
          icon: '/images/chef.png'
        });
      }
    };

    // Handle new menu item added by admin
    const onMenuItemAdded = (data) => {
      const categories = Array.isArray(data.category) ? data.category : [data.category];
      const newItem = {
        id: data.item_id,
        name: data.item_name,
        type: categories[0],
        categories: categories,
        description: data.description || '',
        price: data.price_per_plate,
        image: resolveImageUrl(data.image_url),
        stock: data.stock_quantity !== null ? data.stock_quantity : 100,
        available: data.is_available
      };
      setMenuData(prevMenu => [...prevMenu, newItem]);
    };

    // Handle menu item updated by admin
    const onMenuItemUpdated = (data) => {
      setMenuData(prevMenu => {
        const exists = prevMenu.some((item) => item.id === data.item_id);

        // If item exists and is now unavailable, remove it completely
        if (exists && data.is_available === false) {
          return prevMenu.filter((item) => item.id != data.item_id);
        }

        // If item exists, update it in place
        if (exists) {
          return prevMenu.map(item =>
            item.id === data.item_id
              ? {
                  id: data.item_id,
                  name: data.item_name,
                  type: data.category,
                  description: data.description || '',
                  price: data.price_per_plate,
                  image: resolveImageUrl(data.image_url),
                  stock: data.stock_quantity !== null ? data.stock_quantity : 100,
                  available: data.is_available
                }
              : item
          );
        }

        // If it did not exist and is now available, add it
        if (data.is_available !== false) {
          return [
            ...prevMenu,
            {
              id: data.item_id,
              name: data.item_name,
              type: data.category,
              description: data.description || '',
              price: data.price_per_plate,
              image: resolveImageUrl(data.image_url),
              stock: data.stock_quantity !== null ? data.stock_quantity : 100,
              available: data.is_available,
            }
          ];
        }

        // Otherwise, keep state unchanged
        return prevMenu;
      });
    };

    // Handle menu item deleted by admin
    const onMenuItemDeleted = (data) => {
      setMenuData(prevMenu => prevMenu.filter(item => item.id !== data.item_id));
    };

    // Register all socket listeners
    socketService.on('inventory_changed', onInventoryChange);
    socketService.on('menu_item_added', onMenuItemAdded);
    socketService.on('menu_item_updated', onMenuItemUpdated);
    socketService.on('menu_item_deleted', onMenuItemDeleted);

    return () => {
      socketService.off('inventory_changed', onInventoryChange);
      socketService.off('menu_item_added', onMenuItemAdded);
      socketService.off('menu_item_updated', onMenuItemUpdated);
      socketService.off('menu_item_deleted', onMenuItemDeleted);
    };
  }, []);

  const total = Object.values(cart).reduce(
    (sum, item) => sum + ((item.price || 0) * (item.qty || 0)),
    0
  );

  const cartCount = Object.values(cart).reduce(
    (sum, item) => sum + (item.qty || 0),
    0
  );

  const dedupedMenu = useMemo(() => dedupeMenuItems(menuData), [menuData]);

  const filteredData = useMemo(
    () =>
      dedupedMenu.filter((item) => {
        const matchesSearch = item.name.toLowerCase().includes(search.toLowerCase());
        const matchesFilter = filter === "all" || (item.categories || []).includes(filter);
        return item.available && matchesSearch && matchesFilter;
      }),
    [dedupedMenu, search, filter]
  );

  return (
    <div className="menu-container">
      {/* Header */}
      <div className="menu-header">
        <button className="back-btn" onClick={goBack}>
          ← Back
        </button>
        <h2>Our Menu</h2>
      </div>

      {/* Search and Filter */}
      <div className="menu-controls">
        <input
          type="text"
          placeholder="Search items…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All Items</option>
          <option value="Morning Tiffin Menu">Morning Tiffin Menu</option>
          <option value="Lunch Menu">Lunch Menu</option>
          <option value="Dinner Menu">Dinner Menu</option>
        </select>
      </div>

      {/* Menu Grid */}
      <div className="menu-grid">
        {filteredData.map((item) => (
          <MenuCard
            key={item.id}
            item={item}
            cart={cart}
            updateQty={updateQty}
            addToCart={addToCart}
          />
        ))}
      </div>

      {/* Footer Cart Summary */}
      <div className="cart-footer">
        <p>Items Added: {cartCount}</p>
        <p>Total: ₹{total}</p>
        <button
          className="view-cart-btn"
          onClick={() => goToCart && goToCart()}
        >
          View Cart 🛒
        </button>

      </div>
    </div>
  );
}
