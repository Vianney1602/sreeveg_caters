import React, { useState } from "react";
import axios from "axios";
import "./cart.css";

export default function BulkCartPage({
  bulkCart,
  guestCount,
  updateBulkQty,
  goBack,
  clearCart,
  initiatePayment,
  defaultPaymentMethod,
  paymentStatus,
  clearPaymentStatus,
  bulkOrderCompleted,
  setBulkOrderCompleted,
  bulkOrderedItems,
  setBulkOrderedItems,
}) {
  const items = Object.values(bulkCart).map((item) => ({
    ...item,
    qty: item.qty || guestCount || 1,
  }));

  const subtotal = items.reduce(
    (sum, item) => sum + ((item.price || 0) * (item.qty || 0)),
    0
  );
  const total = subtotal;
  const totalQty = items.reduce((sum, item) => sum + (item.qty || 0), 0);

  const isEmpty = items.length === 0;
  const showSuccess = bulkOrderCompleted && bulkOrderedItems && bulkOrderedItems.length > 0;

  /* 🔹 Checkout State */
  const [showCheckout, setShowCheckout] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    address: "",
  });
  const [paymentMethod, setPaymentMethod] = useState(defaultPaymentMethod || "online"); // 'online' | 'cod'
  const [orderStatus, setOrderStatus] = useState(null); // { type, message, orderId }
  const [isSubmitting, setIsSubmitting] = useState(false); // Prevent duplicate submissions on slow network

  const adjustQty = (id, delta) => {
    const current = bulkCart[id]?.qty || guestCount || 1;
    const nextQty = Math.max(1, current + delta);
    if (typeof updateBulkQty === "function") updateBulkQty(id, nextQty);
  };

  const handleQtyInput = (id, value) => {
    const parsed = parseInt(value, 10);
    const nextQty = Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
    if (typeof updateBulkQty === "function") updateBulkQty(id, nextQty);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePlaceOrder = (e) => {
    e.preventDefault();
    
    // Prevent duplicate submissions during network delay
    if (isSubmitting) {
      return;
    }

    const { name, phone, email, address } = formData;
    if (!name || !phone || !email || !address) {
      setOrderStatus({ type: "error", message: "Please fill all required fields" });
      setTimeout(() => setOrderStatus(null), 4000);
      return;
    }
    
    setIsSubmitting(true);

    // Build payload for backend
    const menu_items = items.map((it) => ({ id: it.id, qty: it.qty, price: it.price }));
    const payload = {
      customer_name: name,
      phone_number: phone,
      email: email,
      event_type: "Bulk Order",
      guests: guestCount,
      event_date: new Date().toISOString().split("T")[0],
      event_time: new Date().toLocaleTimeString(),
      venue: address,
      special: null,
      total_amount: parseFloat(total.toFixed(2)),
      payment_method: paymentMethod,
      menu_items,
    };

    // Optional auth header if customer token exists
    const headers = {};
    try {
      const token = sessionStorage.getItem("_ct");
      if (token) headers.Authorization = `Bearer ${token}`;
    } catch {}

    // COD flow
    if (paymentMethod === "cod") {
      axios
        .post("/api/orders", payload, { headers })
        .then((res) => {
          setOrderStatus({
            type: "success",
            message: "Bulk order placed successfully! Cash on delivery.",
            orderId: res.data.order_id,
          });
          // Save ordered items before clearing cart
          if (typeof setBulkOrderedItems === "function") {
            setBulkOrderedItems(items.map(item => ({
              name: item.name,
              qty: item.qty,
              price: item.price,
              image: item.image
            })));
          }
          if (typeof setBulkOrderCompleted === "function") setBulkOrderCompleted(true);
          setShowCheckout(false);
          setFormData({ name: "", phone: "", email: "", address: "" });
          setPaymentMethod("online");
          if (typeof clearCart === "function") clearCart();
          setTimeout(() => setOrderStatus(null), 5000);
        })
        .catch(() => {
          setOrderStatus({ type: "error", message: "Error placing order. Please try again." });
          setTimeout(() => setOrderStatus(null), 5000);
        })
        .finally(() => {
          setIsSubmitting(false);
        });
      return;
    }

    // Online payment flow (Razorpay)
    axios
      .post("/api/orders", payload, { headers })
      .then((res) => {
        const dbOrderId = res.data.order_id;
        return axios.post("/api/payments/create_order", { order_id: dbOrderId, amount: payload.total_amount });
      })
      .then((rzpRes) => {
        const razorpayOrderId = rzpRes.data.order_id;
        const customerDetails = { name, email, phone };
        if (typeof initiatePayment === "function") {
          initiatePayment(
            razorpayOrderId,
            payload.total_amount,
            customerDetails,
            () => {},
            () => {}
          );
        }
        // Save ordered items before clearing cart
        if (typeof setBulkOrderedItems === "function") {
          setBulkOrderedItems(items.map(item => ({
            name: item.name,
            qty: item.qty,
            price: item.price,
            image: item.image
          })));
        }
        if (typeof setBulkOrderCompleted === "function") setBulkOrderCompleted(true);
        setShowCheckout(false);
        setFormData({ name: "", phone: "", email: "", address: "" });
        setPaymentMethod("online");
        if (typeof clearCart === "function") clearCart();
      })
      .catch(() => {
        setOrderStatus({ type: "error", message: "Error creating payment. Please try again." });
        setTimeout(() => setOrderStatus(null), 5000);
      })
      .finally(() => {
        setIsSubmitting(false);
      });
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

      <div className="cart-content">
        {/* LEFT SIDE */}
        <div className="cart-left">
          {showSuccess ? (
            <div className="empty-cart-container success-container">
              <div className="empty-cart-icon">🎉</div>
              <h3 className="empty-cart-title" style={{color: '#7a0000', fontSize: '2rem', fontWeight: 'bold', letterSpacing: '0.5px', fontFamily: "'Georgia', 'Garamond', serif"}}>Your Bulk Order is Preparing to Get Delivered!</h3>
              <p className="empty-cart-description" style={{color: '#5c0000', fontSize: '1.3rem', fontWeight: '600', marginTop: '15px', fontFamily: "'Trebuchet MS', 'Lucida Grande', sans-serif"}}>
                Thank you for your bulk order! 🙏
              </p>
              <p className="empty-cart-subtitle" style={{color: '#7a0000', marginTop: '10px', fontSize: '1.05rem', fontFamily: "'Segoe UI', Tahoma, sans-serif"}}>
                Our team is preparing your delicious feast with utmost care. Your food will arrive fresh and hot! 🍽️
              </p>
              
              {/* Ordered Items List */}
              {bulkOrderedItems && bulkOrderedItems.length > 0 && (
                <div style={{
                  marginTop: '25px',
                  padding: '20px',
                  backgroundColor: 'rgba(255, 217, 102, 0.15)',
                  borderRadius: '12px',
                  border: '2px solid rgba(122, 0, 0, 0.2)'
                }}>
                  <h4 style={{color: '#7a0000', marginBottom: '15px', fontSize: '1.1rem', fontFamily: "'Georgia', 'Garamond', serif", fontWeight: '600'}}>📋 Your Ordered Items:</h4>
                  {bulkOrderedItems.map((item, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '15px',
                      padding: '12px',
                      marginBottom: '10px',
                      backgroundColor: 'white',
                      borderRadius: '8px',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}>
                      <img 
                        src={item.image} 
                        alt={item.name} 
                        style={{
                          width: '50px',
                          height: '50px',
                          borderRadius: '8px',
                          objectFit: 'cover'
                        }}
                      />
                      <div style={{flex: 1}}>
                        <p style={{color: '#7a0000', fontWeight: '600', margin: '0 0 5px 0'}}>{item.name}</p>
                        <p style={{color: '#5c0000', fontSize: '0.9rem', margin: 0}}>Quantity: {item.qty} × ₹{item.price}</p>
                      </div>
                      <p style={{color: '#7a0000', fontWeight: '700', fontSize: '1rem'}}>₹{(item.qty * item.price).toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              )}
              
              <div style={{
                marginTop: '25px',
                padding: '20px',
                backgroundColor: 'rgba(122, 0, 0, 0.1)',
                borderRadius: '12px',
                borderLeft: '4px solid #7a0000'
              }}>
                <p style={{color: '#5c0000', margin: '10px 0', fontSize: '1.05rem', fontWeight: '600', fontFamily: "'Segoe UI', Tahoma, sans-serif"}}>
                  ✔️ Order Confirmed
                </p>
                <p style={{color: '#5c0000', margin: '10px 0', fontSize: '1.05rem', fontWeight: '600', fontFamily: "'Segoe UI', Tahoma, sans-serif"}}>
                  🍳 Preparing Your Feast
                </p>
                <p style={{color: '#5c0000', margin: '10px 0', fontSize: '1.05rem', fontWeight: '600', fontFamily: "'Segoe UI', Tahoma, sans-serif"}}>
                  🔔 Updates on Your Phone
                </p>
              </div>
              <p style={{color: '#7a0000', marginTop: '20px', fontSize: '1.1rem', fontWeight: '700', fontFamily: "'Trebuchet MS', 'Lucida Grande', sans-serif"}}>
                Status: 🔄 In Progress
              </p>
            </div>
          ) : isEmpty ? (
            <div className="empty-cart-container">
              <div className="empty-cart-icon">🛒</div>
              <h3 className="empty-cart-title">Your Bulk Cart is Empty</h3>
              <p className="empty-cart-description">Looks like you haven't added any items yet!</p>
              <p className="empty-cart-subtitle">Browse our delicious menu and add items to your bulk order</p>
              <button className="empty-cart-cta" onClick={goBack}>
                <span>🍽️</span> Start Ordering
              </button>
              <div className="empty-cart-features">
                <div className="feature-item">
                  <svg className="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M5 12h14M12 5v14M12 5l3 3m-3-3L9 8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="19" r="2"/>
                  </svg>
                  <p>Fast Delivery</p>
                </div>
                <div className="feature-item">
                  <svg className="feature-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                  <p>Fresh Food</p>
                </div>
                <div className="feature-item">
                  <svg className="feature-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2L15.09 8.26H22L17.55 12.74L19.64 19.26L12 14.77L4.36 19.26L6.45 12.74L2 8.26H8.91L12 2Z"/>
                  </svg>
                  <p>Best Taste</p>
                </div>
              </div>
            </div>
          ) : (
            items.map((item) => (
              <div className="cart-item-card" key={item.id}>
                <img
                  src={item.image}
                  alt={item.name}
                  className="cart-item-img"
                />

                <div className="cart-item-info">
                  <h3>{item.name}</h3>
                  <p>{item.qty} persons × ₹{item.price}</p>
                  <div className="qty-row">
                    <button
                      type="button"
                      onClick={() => adjustQty(item.id, -1)}
                      aria-label={`Decrease ${item.name} quantity`}
                    >
                      -
                    </button>
                    <input
                      className="qty-input"
                      type="number"
                      min="1"
                      value={item.qty}
                      onChange={(e) => handleQtyInput(item.id, e.target.value)}
                    />
                    <button
                      type="button"
                      onClick={() => adjustQty(item.id, 1)}
                      aria-label={`Increase ${item.name} quantity`}
                    >
                      +
                    </button>
                  </div>
                </div>

                <div className="cart-price">
                  ₹{(((item.price || 0) * item.qty)).toFixed(2)}
                </div>
              </div>
            ))
          )}
        </div>

        {/* SUMMARY */}
        {!isEmpty && (
          <div className="cart-summary">
            <h3>Order Summary</h3>

            <div className="summary-row">
              <span>Subtotal</span>
              <span>₹{subtotal.toFixed(2)}</span>
            </div>

            <div className="summary-row total">
              <span>Total</span>
              <span className="total-amt">₹{total.toFixed(2)}</span>
            </div>

            <button
              className="checkout-btn"
              disabled={isEmpty || isSubmitting}
              onClick={() => setShowCheckout(true)}
            >
              Proceed to Checkout
            </button>
          </div>
        )}

        {/* SUMMARY ON SUCCESS */}
        {showSuccess && (
          <div className="cart-summary">
            <h3>Order Summary</h3>

            <div className="summary-row">
              <span>Total Items</span>
              <span>{totalQty}</span>
            </div>

            <div className="summary-row">
              <span>Subtotal</span>
              <span>₹{subtotal.toFixed(2)}</span>
            </div>

            <div className="summary-row total">
              <span>Total</span>
              <span className="total-amt">₹{total.toFixed(2)}</span>
            </div>

            <div style={{
              marginTop: '20px',
              padding: '15px',
              backgroundColor: 'rgba(122, 0, 0, 0.1)',
              borderRadius: '8px',
              textAlign: 'center',
              borderLeft: '4px solid #7a0000'
            }}>
              <p style={{color: '#7a0000', margin: '0', fontSize: '0.95rem', fontWeight: '600'}}>
                ✅ Order Confirmed
              </p>
              <p style={{color: '#5c0000', margin: '8px 0 0 0', fontSize: '0.9rem'}}>
                Order ID will be sent via SMS/Email
              </p>
            </div>
          </div>
        )}
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

              {/* Payment method selection */}
              <div className="form-group">
                <label>Payment Method *</label>
                <div className="payment-methods">
                  <label className="payment-option">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="online"
                      checked={paymentMethod === "online"}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    <span className="payment-label">💳 Online Payment (Razorpay)</span>
                  </label>
                  <label className="payment-option">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="cod"
                      checked={paymentMethod === "cod"}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    <span className="payment-label">💵 Cash on Delivery</span>
                  </label>
                </div>
              </div>

              <div className="checkout-summary">
                <div className="summary-line">
                  <span>Total Item Quantity</span>
                  <span>{totalQty}</span>
                </div>
                <div className="summary-line">
                  <span>Base Guest Count</span>
                  <span>{guestCount}</span>
                </div>
                <div className="summary-line total-line">
                  <span>Total Amount</span>
                  <span>₹{total.toFixed(2)}</span>
                </div>
              </div>

              <button type="submit" className="place-order-btn" disabled={isSubmitting}>
                {isSubmitting ? "Processing..." : "Place Bulk Order"}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* ORDER / PAYMENT STATUS POPUP */}
      {(orderStatus || paymentStatus) && (
        <div className="order-status-overlay">
          <div className="order-status-popup">
            <img
              src={`${process.env.PUBLIC_URL}/images/chef.png`}
              alt="Order Status"
              className={`order-status-image ${(orderStatus || paymentStatus).type}`}
              onError={(e) => {
                e.target.src = "/images/biriyani.png";
              }}
            />
            <div className="order-status-content">
              <div className={`status-icon ${(orderStatus || paymentStatus).type}`}>
                {(orderStatus || paymentStatus).type === "success" ? "✅" : "❌"}
              </div>
              <h3 className={`status-title ${(orderStatus || paymentStatus).type}`}>
                {(orderStatus || paymentStatus).type === "success" ? "Order Placed Successfully!" : "Order Failed"}
              </h3>
              <p className="status-message">{(orderStatus || paymentStatus).message}</p>
              {(orderStatus || paymentStatus).orderId && (
                <p className="order-id">
                  Order ID: <strong>{(orderStatus || paymentStatus).orderId}</strong>
                </p>
              )}
              <button
                className="status-close-btn"
                onClick={() => {
                  if (orderStatus) setOrderStatus(null);
                  if (paymentStatus && clearPaymentStatus) clearPaymentStatus();
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}