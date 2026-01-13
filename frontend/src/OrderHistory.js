import React, { useState, useEffect } from "react";
import axios from "axios";
import "./home.css";

export default function OrderHistory({ goBack, user }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const token = sessionStorage.getItem('_userToken');
      if (!token) {
        setError('Please sign in to view order history');
        setLoading(false);
        return;
      }

      const response = await axios.get('/api/users/order-history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setOrders(response.data.orders);
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load order history');
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending': return '#fbbf24';
      case 'confirmed': return '#3b82f6';
      case 'preparing': return '#f97316';
      case 'ready': return '#10b981';
      case 'delivered': return '#059669';
      case 'completed': return '#16a34a';
      case 'cancelled': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="order-history-container">
        <div className="order-history-header">
          <button className="back-btn" onClick={goBack}>← Back</button>
          <h2>Order History</h2>
        </div>
        <div className="loading-text">Loading your orders...</div>
      </div>
    );
  }

  return (
    <div className="order-history-container">
      <div className="order-history-header">
        <button className="back-btn" onClick={goBack}>← Back</button>
        <h2>Order History</h2>
      </div>

      {error && <div className="auth-error">{error}</div>}

      {orders.length === 0 ? (
        <div className="no-orders">
          <p>You haven't placed any orders yet.</p>
          <button onClick={goBack}>Start Ordering</button>
        </div>
      ) : (
        <div className="orders-list">
          {orders.map((order) => (
            <div key={order.order_id} className="order-card">
              <div className="order-header">
                <div>
                  <h3>Order #{order.order_id}</h3>
                  <p className="order-date">
                    {new Date(order.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
                <div 
                  className="order-status"
                  style={{ 
                    background: getStatusColor(order.status),
                    color: '#fff',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontWeight: 'bold'
                  }}
                >
                  {order.status}
                </div>
              </div>

              <div className="order-details">
                {order.event_type && (
                  <div className="order-detail-item">
                    <strong>Event Type:</strong> {order.event_type}
                  </div>
                )}
                {order.number_of_guests && (
                  <div className="order-detail-item">
                    <strong>Guests:</strong> {order.number_of_guests}
                  </div>
                )}
                {order.event_date && (
                  <div className="order-detail-item">
                    <strong>Event Date:</strong> {order.event_date}
                  </div>
                )}
                {order.event_time && (
                  <div className="order-detail-item">
                    <strong>Event Time:</strong> {order.event_time}
                  </div>
                )}
                {order.venue_address && (
                  <div className="order-detail-item">
                    <strong>Venue:</strong> {order.venue_address}
                  </div>
                )}
                <div className="order-detail-item">
                  <strong>Payment Method:</strong> {order.payment_method === 'online' ? 'Online' : 'Cash on Delivery'}
                </div>
              </div>

              {order.items && order.items.length > 0 && (
                <div className="order-items">
                  <strong>Items:</strong>
                  <ul>
                    {order.items.map((item, idx) => (
                      <li key={idx}>
                        {item.item_name} x {item.quantity} - ₹{item.price}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="order-total">
                <strong>Total Amount:</strong> ₹{order.total_amount.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
