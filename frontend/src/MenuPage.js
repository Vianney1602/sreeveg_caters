import React, { useState, useEffect } from "react";
import axios from "axios";
import socketService from "./services/socketService";
import MenuCard from "./MenuCard";
import "./menu.css";

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
        const items = res.data.map(item => ({
          id: item.item_id,
          name: item.item_name,
          type: item.category,
          description: item.description || '',
          price: item.price_per_plate,
          image: resolveImageUrl(item.image_url),
          stock: item.stock_quantity !== null ? item.stock_quantity : 100,
          available: item.is_available
        }));
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
      const newItem = {
        id: data.item_id,
        name: data.item_name,
        type: data.category,
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
      setMenuData(prevMenu =>
        prevMenu.map(item =>
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
        )
      );
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

  const filteredData = menuData.filter((item) => {
    return (
      item.available &&
      item.name.toLowerCase().includes(search.toLowerCase()) &&
      (filter === "all" || item.type === filter)
    );
  });

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
          <option value="starter">Starters</option>
          <option value="main">Main Course</option>
          <option value="dessert">Desserts</option>
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
