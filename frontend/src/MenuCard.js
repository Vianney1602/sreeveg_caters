import React from "react";

const MenuCard = React.memo(({ item, cart, updateQty, addToCart }) => {
  const qty = cart[item.id]?.qty || 0;

  return (
    <div className="menu-card">
      <img src={item.image} alt={item.name} className="menu-img" loading="lazy" />

      <h3 className="menu-title">{item.name}</h3>
      <p className="menu-desc">{item.description}</p>

      <p className="menu-price">
        ₹ {item.price} <span>/plate</span>
      </p>

      <div className="qty-controls">
        <button onClick={() => qty > 0 && updateQty(item.id, qty - 1)}>−</button>
        <span>{qty}</span>
        <button onClick={() => updateQty(item.id, qty + 1)}>+</button>
      </div>

      <button
        className={`add-btn ${qty > 0 ? "active" : ""}`}
        onClick={() => qty === 0 && addToCart(item)}
      >
        {qty > 0 ? `✓ Added (${qty})` : "Add to Cart"}
      </button>
    </div>
  );
});

export default MenuCard;
