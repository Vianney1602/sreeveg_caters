import React, { useEffect, useState } from "react";
import axios from "axios";
import socketService from "./services/socketService";
import "./menu.css";



export default function BulkMenuPage({
  guestCount,
  bulkCart,
  setBulkCart,
  goToCart,
  goBack,
}) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");

  const [menuItems, setMenuItems] = useState([]);
  
  // Helper to resolve image URLs correctly
  const resolveImageUrl = (url) => {
    if (!url) return '/images/chef.png';
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
    
    // If it starts with /static, static, /uploads or uploads, treat as backend asset
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
    
    // Otherwise, assume it's a relative path and prefix with backend base
    return toBackendUrl(trimmed);
  };
  
  useEffect(() => {
    axios
      .get("/api/menu_items")
      .then((res) => {
        const items = (res.data || []).map((m) => ({
          id: m.item_id,
          name: m.item_name,
          type: m.category || "",
          price: m.price_per_plate || 0,
          image: resolveImageUrl(m.image_url),
          description: m.description || "",
          available: m.is_available !== false,
        }));
        setMenuItems(items);
      })
      .catch(() => setMenuItems([]));
  }, []);

  // Keep menu in sync with admin changes
  useEffect(() => {
    const onMenuItemAdded = (data) => {
      setMenuItems((prev) => ([
        ...prev,
        {
          id: data.item_id,
          name: data.item_name,
          type: data.category || "",
          price: data.price_per_plate || 0,
          image: resolveImageUrl(data.image_url),
          description: data.description || "",
          available: data.is_available,
        }
      ]));
    };

    const onMenuItemUpdated = (data) => {
      setMenuItems((prev) => {
        const exists = prev.some((item) => item.id === data.item_id);

        // If it exists and is now unavailable, remove it
        if (exists && data.is_available === false) {
          return prev.filter((item) => item.id !== data.item_id);
        }

        // If it exists, update it
        if (exists) {
          return prev.map((item) => (
            item.id === data.item_id
              ? {
                  id: data.item_id,
                  name: data.item_name,
                  type: data.category || "",
                  price: data.price_per_plate || 0,
                  image: resolveImageUrl(data.image_url),
                  description: data.description || "",
                  available: data.is_available,
                }
              : item
          ));
        }

        // If it did not exist and is now available, add it
        if (data.is_available !== false) {
          return [
            ...prev,
            {
              id: data.item_id,
              name: data.item_name,
              type: data.category || "",
              price: data.price_per_plate || 0,
              image: resolveImageUrl(data.image_url),
              description: data.description || "",
              available: data.is_available,
            }
          ];
        }

        return prev;
      });
    };

    const onMenuItemDeleted = (data) => {
      setMenuItems((prev) => prev.filter((item) => item.id !== data.item_id));
    };

    socketService.on('menu_item_added', onMenuItemAdded);
    socketService.on('menu_item_updated', onMenuItemUpdated);
    socketService.on('menu_item_deleted', onMenuItemDeleted);

    return () => {
      socketService.off('menu_item_added', onMenuItemAdded);
      socketService.off('menu_item_updated', onMenuItemUpdated);
      socketService.off('menu_item_deleted', onMenuItemDeleted);
    };
  }, []);

  const toggleItem = (item) => {
    setBulkCart((prev) => {
      const copy = { ...prev };
      if (copy[item.id]) delete copy[item.id];
      else copy[item.id] = item;
      return copy;
    });
  };

  const total = Object.values(bulkCart).reduce(
    (sum, item) => sum + ((item.price || 0) * guestCount),
    0
  );

  const cartCount = Object.keys(bulkCart).length;

  const filteredData = menuItems.filter((item) => {
    return (
      item.available &&
      item.name.toLowerCase().includes(search.toLowerCase()) &&
      (filter === "all" || item.type === filter)
    );
  });

  return (
    <div className="menu-container">
      <div className="menu-header">
        <button className="back-btn" onClick={goBack}>← Back</button>
        <h2>Bulk Order Menu</h2>
        <span>{guestCount} Persons</span>
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
          <option value="Lunch Menu - Regular Meals">Lunch Menu - Regular Meals</option>
          <option value="Lunch Menu - Mini Meals">Lunch Menu - Mini Meals</option>
          <option value="Lunch Menu - Variety Rice">Lunch Menu - Variety Rice</option>
          <option value="Dinner Menu">Dinner Menu</option>
        </select>
      </div>

      <div className="menu-grid">
        {filteredData.map((item) => (
          <div key={item.id} className="menu-card">
            <div className="menu-img-box">
  <img src={item.image} alt={item.name} />
</div>

            <h3 className="menu-title">{item.name}</h3>
            <p className="menu-desc">{item.description}</p>
            <p className="menu-price">₹{item.price} / person</p>

            <button
              className={`add-btn ${bulkCart[item.id] ? "selected" : ""}`}
              onClick={() => toggleItem(item)}
            >
              {bulkCart[item.id] ? "Selected" : "Add to Bulk Order"}
            </button>
          </div>
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