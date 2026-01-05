import React, { useState } from "react";
import axios from "axios";
import "./cart.css";

export default function BulkCartPage({
  bulkCart,
  guestCount,
  goBack,
  clearCart,
  initiatePayment,
  defaultPaymentMethod,
  paymentStatus,
  clearPaymentStatus,
}) {
  const items = Object.values(bulkCart);

  const subtotal = items.reduce(
    (sum, item) => sum + item.price * guestCount,
    0
  );
  const total = subtotal;

  const isEmpty = items.length === 0;

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
    const menu_items = items.map((it) => ({ id: it.id, qty: guestCount, price: it.price }));
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
                  <span>Total Guests</span>
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