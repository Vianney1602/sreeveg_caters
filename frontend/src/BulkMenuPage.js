import React, { useEffect, useState } from "react";
import axios from "axios";
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
    
    // Get backend base URL from environment or default
    const backendBase = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
    
    // If it starts with /static or /api, it's a backend URL
    if (trimmed.startsWith('/static') || trimmed.startsWith('/api')) {
      return `${backendBase}${trimmed}`;
    }
    
    // If it starts with /images, it's a frontend public image
    if (trimmed.startsWith('/images')) {
      const base = process.env.PUBLIC_URL || '';
      return `${base}${trimmed}`;
    }
    
    // Otherwise, assume it's a relative path and prefix with backend base
    return `${backendBase}${trimmed.startsWith('/') ? '' : '/'}${trimmed}`;
  };
  
  useEffect(() => {
    axios
      .get("/api/menu_items")
      .then((res) => {
        const items = (res.data || []).map((m) => ({
          id: m.item_id,
          name: m.item_name,
          type: (m.category || "main").toLowerCase(),
          price: m.price_per_plate || 0,
          image: resolveImageUrl(m.image_url),
          description: m.description || "",
        }));
        setMenuItems(items);
      })
      .catch(() => setMenuItems([]));
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
          <option value="starter">Starters</option>
          <option value="main">Main Course</option>
          <option value="dessert">Desserts</option>
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