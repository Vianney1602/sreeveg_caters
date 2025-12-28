import React, { useState } from "react";
import "./menu.css";

const bulkMenuItems = [
  {
    id: 1,
    name: "Veg Meals",
    type: "main",
    price: 140,
    image: "/images/meals_veg.png",
    description: "South Indian rice platter with curries and sides.",
  },
  {
    id: 2,
    name: "Paneer Butter Masala",
    type: "main",
    price: 120,
    image: "/images/panner_butter_masala.png",
    description: "Rich paneer gravy with butter & spices.",
  },
  {
    id: 3,
    name: "Veg Biriyani",
    type: "main",
    price: 180,
    image: "/images/veg-biriyani.webp",
    description: "Aromatic basmati rice with vegetables.",
  },
  {
      id: 5,
      name: "Chole Puri",
      type: "main",
      description: "Spiced chickpeas served with fluffy puris.",
      price: 100,
      image: "/images/chola_puri.png",
    },
    {
      id: 7,
      name: "Dal Makhani",
      type: "main",
      description: "Slow-cooked black lentils finished with cream.",
      price: 130,
      image: "/images/dhal_makini.png",
    },
    {
      id: 11,
      name: "Paneer Tikka",
      type: "starter",
      description: "Smoky marinated paneer skewers.",
      price: 110,
      image: "/images/paneer-tikka.jpg",
    },
    {
      id: 12,
      name: "Veg Cutlet",
      type: "starter",
      description: "Crispy vegetable patties with herbs.",
      price: 90,
      image: "/images/veg-cutlet.webp",
    },
    {
      id: 13,
      name: "Gulab Jamun",
      type: "dessert",
      description: "Soft milk dumplings soaked in syrup.",
      price: 80,
      image: "/images/gulab-jamun.jpg",
    },
    {
      id: 14,
      name: "Rasmalai",
      type: "dessert",
      description: "Cottage cheese patties in saffron milk.",
      price: 90,
      image: "/images/rasamalai.webp",
    },
];

export default function BulkMenuPage({
  guestCount,
  bulkCart,
  setBulkCart,
  goToCart,
  goBack,
}) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");

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

  const filteredData = bulkMenuItems.filter((item) => {
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