import React, { useState } from "react";
import "./cart.css";

export default function BulkCartPage({
  bulkCart,
  guestCount,
  goBack,
}) {
  const items = Object.values(bulkCart);

  const subtotal = items.reduce(
    (sum, item) => sum + item.price * guestCount,
    0
  );
  const tax = subtotal * 0.05;
  const total = subtotal + tax;

  const isEmpty = items.length === 0;

  /* 🔹 Checkout State */
  const [showCheckout, setShowCheckout] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    address: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePlaceOrder = (e) => {
    e.preventDefault();

    const { name, phone, email, address } = formData;
    if (!name || !phone || !email || !address) {
      alert("Please fill all details");
      return;
    }

    alert(`Bulk Order Placed Successfully!\nTotal: ₹${total.toFixed(2)}`);
    setShowCheckout(false);
    setFormData({ name: "", phone: "", email: "", address: "" });
  };

  return (
    <div className="cart-container">
      {/* HEADER */}
      <div className="cart-header">
        <button className="back-btn" onClick={goBack}>
          ← Back
        </button>
        <h2>Bulk Order Cart</h2>
      </div>

      {/* EMPTY CART */}
      {isEmpty && (
        <div className="empty-cart-message">
          <p>Your cart is empty 🛒</p>
        </div>
      )}

      <div className="cart-content">
        {/* LEFT SIDE */}
        <div className="cart-left">
          {!isEmpty &&
            items.map((item) => (
              <div className="cart-item-card" key={item.id}>
                <img
                  src={item.image}
                  alt={item.name}
                  className="cart-item-img"
                />

                <div className="cart-item-info">
                  <h3>{item.name}</h3>
                  <p>{guestCount} persons × ₹{item.price}</p>
                </div>

                <div className="cart-price">
                  ₹{(item.price * guestCount).toFixed(2)}
                </div>
              </div>
            ))}
        </div>

        {/* SUMMARY */}
        <div className="cart-summary">
          <h3>Order Summary</h3>

          <div className="summary-row">
            <span>Subtotal</span>
            <span>₹{subtotal.toFixed(2)}</span>
          </div>

          <div className="summary-row">
            <span>Tax (5%)</span>
            <span>₹{tax.toFixed(2)}</span>
          </div>

          <div className="summary-row total">
            <span>Total</span>
            <span className="total-amt">₹{total.toFixed(2)}</span>
          </div>

          <button
            className="checkout-btn"
            disabled={isEmpty}
            onClick={() => setShowCheckout(true)}
          >
            Proceed to Checkout
          </button>
        </div>
      </div>

      {/* 🔹 CHECKOUT MODAL */}
      {showCheckout && (
        <div className="checkout-overlay">
          <div
            className="checkout-backdrop"
            onClick={() => setShowCheckout(false)}
          />

          <div className="checkout-modal">
            <div className="checkout-header">
              <h2>Bulk Order Details</h2>
              <button
                className="close-checkout-btn"
                onClick={() => setShowCheckout(false)}
              >
                ✖
              </button>
            </div>

            <form className="checkout-form" onSubmit={handlePlaceOrder}>
              <div className="form-group">
                <label>Full Name *</label>
                <input
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Phone Number *</label>
                <input
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Delivery Address *</label>
                <textarea
                  name="address"
                  rows="3"
                  value={formData.address}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="checkout-summary">
                <div className="summary-line">
                  <span>Total Guests</span>
                  <span>{guestCount}</span>
                </div>
                <div className="summary-line total-line">
                  <span>Total Amount</span>
                  <span>₹{total.toFixed(2)}</span>
                </div>
              </div>

              <button type="submit" className="place-order-btn">
                Place Bulk Order
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}