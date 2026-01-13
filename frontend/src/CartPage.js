import React, { useState } from "react";
import axios from "axios";
import "./cart.css";

export default function CartPage({ goBack, cart, updateQty, clearCart, initiatePayment, paymentStatus, clearPaymentStatus, orderCompleted, setOrderCompleted, orderedItems, setOrderedItems }) {
  const [showCheckout, setShowCheckout] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    address: ''
  });
  const [paymentMethod, setPaymentMethod] = useState('online'); // 'online' or 'cod'
  const [orderResult, setOrderResult] = useState(null);
  const [orderStatus, setOrderStatus] = useState(null); // { type: 'success'|'error', message: string }
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false); // Prevent duplicate submissions on slow network

  const cartItems = Object.values(cart);

  const subtotal = Object.values(cart).reduce((sum, item) => {
    const price = item.price || 0;
    const qty = item.qty || 0;
    return sum + (price * qty);
  }, 0);

  const total = subtotal;

  const isEmpty = cartItems.length === 0;
  const showSuccess = orderCompleted && orderedItems && orderedItems.length > 0;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCheckout = (e) => {
    e.preventDefault();
    
    // Prevent duplicate submissions during network delay
    if (isSubmitting) {
      return;
    }
    
    if (!(formData.name && formData.phone && formData.email && formData.address)) {
      setFormError('Please fill all required fields');
      return;
    }
    setFormError(''); // Clear error if form is valid
    setIsSubmitting(true);

    // Build payload to match backend expectations
    const payload = {
      customer_name: formData.name,
      phone_number: formData.phone,
      email: formData.email,
      event_type: "Delivery",
      guests: 1,
      event_date: new Date().toISOString().split('T')[0],
      event_time: new Date().toLocaleTimeString(),
      venue: formData.address,
      special: null,
      total_amount: parseFloat(total.toFixed(2)),
      payment_method: paymentMethod, // Add payment method to payload
      menu_items: cartItems.map(i => ({ id: i.id, qty: i.qty, price: i.price }))
    };

    // attach customer_id and Authorization header when user is logged in
    const customer = (() => {
      try { return JSON.parse(sessionStorage.getItem('_user')); } catch { return null; }
    })();
    if (customer && customer.customer_id) payload.customer_id = customer.customer_id;

    const headers = {};
    const userToken = sessionStorage.getItem('_userToken'); // User auth token
    if (userToken) headers.Authorization = `Bearer ${userToken}`;

    if (paymentMethod === 'cod') {
      // Cash on Delivery - place order directly
      axios.post('/api/orders', payload, { headers })
        .then(res => {
          setOrderStatus({
            type: 'success',
            message: 'Order placed successfully! You will pay cash on delivery.',
            orderId: res.data.order_id
          });
          // Save ordered items before clearing cart
          setOrderedItems(cartItems.map(item => ({
            name: item.name,
            qty: item.qty,
            price: item.price,
            image: item.image
          })));
          setOrderCompleted(true);
          setShowCheckout(false);
          setFormData({ name: '', phone: '', email: '', address: '' });
          setPaymentMethod('online'); // Reset to default
          // Clear cart in parent if provided
          if (typeof clearCart === 'function') clearCart();
        })
        .catch(err => {
          console.error('Order placement error:', err);
          const errorMsg = err.response?.data?.error || err.message || 'Error placing order. Please try again.';
          setOrderStatus({
            type: 'error',
            message: errorMsg
          });
          // Auto-hide error message after 5 seconds
          setTimeout(() => setOrderStatus(null), 5000);
        })
        .finally(() => {
          setIsSubmitting(false);
        });
    } else {
      // Online Payment - proceed with Razorpay
      axios.post('/api/orders', payload, { headers })
        .then(res => {
          const dbOrderId = res.data.order_id;
          const amount = payload.total_amount;
          // Create Razorpay order
          return axios.post('/api/payments/create_order', {
            order_id: dbOrderId,
            amount: amount
          });
        })
        .then(rzpRes => {
          const razorpayOrderId = rzpRes.data.order_id;
          const amount = payload.total_amount;
          const customerDetails = {
            name: formData.name,
            email: formData.email,
            phone: formData.phone
          };
          initiatePayment(razorpayOrderId, amount, customerDetails,
            (orderId) => {
              // Payment success callback - handled by App.js paymentStatus
              // Save ordered items before clearing cart
              setOrderedItems(cartItems.map(item => ({
                name: item.name,
                qty: item.qty,
                price: item.price,
                image: item.image
              })));
              setOrderCompleted(true);
              setShowCheckout(false);
              setFormData({ name: '', phone: '', email: '', address: '' });
              setPaymentMethod('online'); // Reset to default
              // Clear cart in parent if provided
              if (typeof clearCart === 'function') clearCart();
            },
            (errorMessage) => {
              // Payment error callback - handled by App.js paymentStatus
              setShowCheckout(false);
              setFormData({ name: '', phone: '', email: '', address: '' });
              setPaymentMethod('online'); // Reset to default
            }
          );
          // Save ordered items before clearing cart
          setOrderedItems(cartItems.map(item => ({
            name: item.name,
            qty: item.qty,
            price: item.price,
            image: item.image
          })));
          setOrderCompleted(true);
          setShowCheckout(false);
          setFormData({ name: '', phone: '', email: '', address: '' });
          setPaymentMethod('online'); // Reset to default
          // Clear cart in parent if provided
          if (typeof clearCart === 'function') clearCart();
        })
        .catch(err => {
          console.error('Payment order creation error:', err);
          const errorMsg = err.response?.data?.error || err.message || 'Error placing order or creating payment. Please try again.';
          setOrderStatus({
            type: 'error',
            message: errorMsg
          });
          // Auto-hide error message after 5 seconds
          setTimeout(() => setOrderStatus(null), 5000);
        })
        .finally(() => {
          setIsSubmitting(false);
        });
    }
  };

  return (
    <div className="cart-container">
      {/* Header */}
      <div className="cart-header">
        <button className="back-btn" onClick={goBack}>← Back</button>
        <h2>Your Cart</h2>
      </div>

      <div className="cart-content">
        {/* LEFT SIDE */}
        <div className="cart-left">

          {showSuccess ? (
            <div className="empty-cart-container success-container">
              <div className="empty-cart-icon">🎉</div>
              <h3 className="empty-cart-title" style={{color: '#7a0000', fontSize: '2rem', fontWeight: 'bold', letterSpacing: '0.5px', fontFamily: "'Georgia', 'Garamond', serif"}}>Your Order is Preparing to Get Delivered!</h3>
              <p className="empty-cart-description" style={{color: '#5c0000', fontSize: '1.3rem', fontWeight: '600', marginTop: '15px', fontFamily: "'Trebuchet MS', 'Lucida Grande', sans-serif"}}>
                Thank you for your order! 🙏
              </p>
              <p className="empty-cart-subtitle" style={{color: '#7a0000', marginTop: '10px', fontSize: '1.05rem', fontFamily: "'Segoe UI', Tahoma, sans-serif"}}>
                Our team is preparing your delicious meal with utmost care. Your food will arrive fresh and hot! 🍽️
              </p>
              
              {/* Ordered Items List */}
              {orderedItems && orderedItems.length > 0 && (
                <div style={{
                  marginTop: '25px',
                  padding: '20px',
                  backgroundColor: 'rgba(255, 217, 102, 0.15)',
                  borderRadius: '12px',
                  border: '2px solid rgba(122, 0, 0, 0.2)'
                }}>
                  <h4 style={{color: '#7a0000', marginBottom: '15px', fontSize: '1.1rem', fontFamily: "'Georgia', 'Garamond', serif", fontWeight: '600'}}>📋 Your Ordered Items:</h4>
                  {orderedItems.map((item, index) => (
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
            </div>
          ) : isEmpty ? (
            <div className="empty-cart-container">
              <div className="empty-cart-icon">🛒</div>
              <h3 className="empty-cart-title">Your Cart is Empty</h3>
              <p className="empty-cart-description">Looks like you haven't added anything yet!</p>
              <p className="empty-cart-subtitle">Browse our delicious menu and add items to your cart</p>
              <button className="empty-cart-cta" onClick={goBack}>
                <span>🍽️</span> Start Shopping
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
            <>
              {/* ONLY show items when NOT empty */}
              {cartItems.map((item) => (
                <div className="cart-item-card" key={item.id}>
                
                {/* DELETE BUTTON */}
                <button className="delete-btn" onClick={() => updateQty(item.id, 0)}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 6h18v2H3V6zm2 3h14l-1.5 12.5a2 2 0 0 1-2 1.5H8.5a2 2 0 0 1-2-1.5L5 9zm5-5h4l1 1h5v2H4V5h5l1-1z" />
                  </svg>
                </button>

              <img src={item.image} alt={item.name} className="cart-item-img" />

              <div className="cart-item-info">
                <h3>{item.name}</h3>
                <p>{item.description}</p>

                <div className="qty-row">
                  <button onClick={() => updateQty(item.id, item.qty - 1)}>−</button>
                  <span>{item.qty}</span>
                  <button onClick={() => updateQty(item.id, item.qty + 1)}>+</button>
                </div>
              </div>

              <div className="cart-price">
                ₹{(item.qty * item.price).toFixed(2)}
              </div>
            </div>
          ))}

            </>
          )}
        </div>

        {/* SUMMARY SECTION (still shown even if empty) */}
        {!showSuccess && (
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
              disabled={isEmpty}
              onClick={() => setShowCheckout(true)}
            >
              {isEmpty ? "No items to checkout" : "Proceed to Checkout"}
            </button>
          </div>
        )}

        {/* SUMMARY ON SUCCESS */}
        {showSuccess && (
          <div className="cart-summary">
            <h3>Order Summary</h3>

            {/* Ordered Items in Summary */}
            {orderedItems && orderedItems.length > 0 && (
              <div style={{
                marginBottom: '20px',
                paddingBottom: '20px',
                borderBottom: '1px solid #e0e0e0'
              }}>
                <h4 style={{color: '#7a0000', fontSize: '0.95rem', fontWeight: '600', marginBottom: '12px', fontFamily: "'Georgia', 'Garamond', serif"}}>Items Ordered:</h4>
                {orderedItems.map((item, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 0',
                    fontSize: '0.9rem',
                    borderBottom: index < orderedItems.length - 1 ? '1px solid #f0f0f0' : 'none'
                  }}>
                    <div style={{flex: 1}}>
                      <p style={{color: '#5c0000', fontWeight: '600', margin: '0 0 3px 0'}}>{item.name}</p>
                      <p style={{color: '#7a0000', fontSize: '0.85rem', margin: 0}}>Qty: {item.qty} × ₹{item.price}</p>
                    </div>
                    <p style={{color: '#7a0000', fontWeight: '700', marginLeft: '10px'}}>₹{(item.qty * item.price).toFixed(2)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* CHECKOUT MODAL */}
      {showCheckout && (
        <div className="checkout-overlay">
          <div className="checkout-backdrop" onClick={() => setShowCheckout(false)} />
          <div className="checkout-modal">
            <div className="checkout-header">
              <h2>Order Details</h2>
              <button 
                className="close-checkout-btn"
                onClick={() => setShowCheckout(false)}
              >
                ✖
              </button>
            </div>

            <div className="checkout-content">
              <form onSubmit={handleCheckout} className="checkout-form">
                {formError && (
                  <div className="form-error-banner">
                    ⚠️ {formError}
                  </div>
                )}
                <div className="form-group">
                  <label>Full Name *</label>
                  <input 
                    type="text" 
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Enter your name" 
                    required 
                  />
                </div>

                <div className="form-group">
                  <label>Phone Number *</label>
                  <input 
                    type="tel" 
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="Enter your phone" 
                    required 
                  />
                </div>

                <div className="form-group">
                  <label>Email Address *</label>
                  <input 
                    type="email" 
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email" 
                    required 
                  />
                </div>

                <div className="form-group">
                  <label>Delivery Address *</label>
                  <textarea 
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    placeholder="Enter complete delivery address" 
                    rows="4"
                    required
                  ></textarea>
                </div>

                {/* PAYMENT METHOD SELECTION */}
                <div className="form-group">
                  <label>Payment Method *</label>
                  <div className="payment-methods">
                    <label className="payment-option">
                      <input
                        type="radio"
                        name="paymentMethod"
                        value="online"
                        checked={paymentMethod === 'online'}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                      />
                      <span className="payment-label">
                        💳 Online Payment (Razorpay)
                      </span>
                    </label>
                    <label className="payment-option">
                      <input
                        type="radio"
                        name="paymentMethod"
                        value="cod"
                        checked={paymentMethod === 'cod'}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                      />
                      <span className="payment-label">
                        💵 Cash on Delivery
                      </span>
                    </label>
                  </div>
                </div>

                <div className="checkout-summary">

                  <div className="summary-line total-line">
                    <span>Total Amount</span>
                    <span>₹{total.toFixed(2)}</span>
                  </div>
                </div>

                <button type="submit" className="place-order-btn" disabled={isSubmitting}>
                  {isSubmitting ? 'Processing...' : 'Place Order'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* ORDER STATUS POPUP */}
      {(orderStatus || paymentStatus) && (
        <div className="order-status-overlay">
          <div className="order-status-popup">
            {(orderStatus || paymentStatus) && (
              <img 
                src={`${process.env.PUBLIC_URL}/images/chef.png`} 
                alt="Order Status" 
                className={`order-status-image ${(orderStatus || paymentStatus).type}`}
                onError={(e) => {
                  e.target.src = '/images/biriyani.png';
                }}
              />
            )}
            <div className="order-status-content">
              <div className={`status-icon ${(orderStatus || paymentStatus).type}`}>
                {(orderStatus || paymentStatus).type === 'success' ? '✅' : '❌'}
              </div>
              <h3 className={`status-title ${(orderStatus || paymentStatus).type}`}>
                {(orderStatus || paymentStatus).type === 'success' ? 'Order Placed Successfully!' : 'Order Failed'}
              </h3>
              <p className="status-message">{(orderStatus || paymentStatus).message}</p>
              {(orderStatus || paymentStatus).orderId && (
                <p className="order-id">Order ID: <strong>{(orderStatus || paymentStatus).orderId}</strong></p>
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

      {/* PROCESSING OVERLAY - Show while order is being placed */}
      {isSubmitting && (
        <div className="processing-overlay">
          <div className="processing-popup">
            <div className="spinner-container">
              <div className="spinner"></div>
            </div>
            <h3 className="processing-title">Processing Your Order...</h3>
            <p className="processing-message">Please wait while we confirm your order</p>
          </div>
        </div>
      )}

      {/* ORDER SUMMARY (shown after successful order) */}
      {orderResult && (
        <div className="order-summary">
          <div className="summary-card">
            <h2>Order Placed Successfully</h2>
            <p><strong>Order ID:</strong> {orderResult.order_id}</p>
            <p><strong>Name:</strong> {orderResult.name}</p>
            <p><strong>Phone:</strong> {orderResult.phone}</p>
            <p><strong>Address:</strong> {orderResult.address}</p>

            <h3>Items</h3>
            <ul>
              {orderResult.items.map(it => (
                <li key={it.id}>{it.name} × {it.qty} — ₹{(it.price * it.qty).toFixed(2)}</li>
              ))}
            </ul>

            <div className="summary-line total-line">
              <span>Total</span>
              <span>₹{orderResult.total.toFixed(2)}</span>
            </div>

            <button className="close-summary-btn" onClick={() => setOrderResult(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
