import React, { useState, useEffect } from "react";
import axios from "axios";
import socketService from "./services/socketService";
import "./home.css";

export default function OrderHistory({ goBack, user }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [cancelLoading, setCancelLoading] = useState(false);

  useEffect(() => {
    fetchOrders();
    
    // Connect to socket and listen for order status changes
    socketService.connect();
    
    const handleStatusChange = (data) => {
      // Update order status in real-time if it belongs to this user
      if (user && data.customer_id === user.id) {
        setOrders(prevOrders => 
          prevOrders.map(order => 
            order.order_id === data.order_id 
              ? { ...order, status: data.new_status }
              : order
          )
        );
      }
    };
    
    socketService.on('order_status_changed', handleStatusChange);
    
    return () => {
      socketService.off('order_status_changed', handleStatusChange);
    };
  }, [user]);

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
      case 'out for delivery': return '#f97316';
      case 'delivered': return '#059669';
      case 'cancelled': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const handleCancelClick = (order) => {
    setSelectedOrder(order);
    setShowCancelConfirm(true);
  };

  const handleCancelConfirm = async () => {
    if (!selectedOrder) return;
    
    setCancelLoading(true);
    setError('');
    
    try {
      const token = sessionStorage.getItem('_userToken');
      const response = await axios.post(
        `/api/orders/${selectedOrder.order_id}/request-cancel`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert(response.data.message || 'Cancellation request sent to admin. You will be notified once approved.');
      setShowCancelConfirm(false);
      setSelectedOrder(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to request cancellation');
      alert(err.response?.data?.error || 'Failed to request cancellation');
    } finally {
      setCancelLoading(false);
    }
  };

  const canCancelOrder = (order) => {
    const status = order.status?.toLowerCase();
    return status !== 'delivered' && status !== 'cancelled';
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

              {canCancelOrder(order) && (
                <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                  <button
                    onClick={() => handleCancelClick(order)}
                    style={{
                      background: '#dc2626',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '0.75rem 2rem',
                      fontSize: '1rem',
                      fontWeight: '700',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.background = '#b91c1c';
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 6px 16px rgba(220, 38, 38, 0.4)';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = '#dc2626';
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 4px 12px rgba(220, 38, 38, 0.3)';
                    }}
                  >
                    Cancel Order
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Cancellation Confirmation Modal */}
      {showCancelConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#fff',
            borderRadius: '16px',
            padding: '2rem',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
            border: '2px solid #d4af37'
          }}>
            <h3 style={{ color: '#7a0000', marginTop: 0, marginBottom: '1rem' }}>
              Confirm Order Cancellation
            </h3>
            <p style={{ color: '#4a4a4a', lineHeight: '1.6', marginBottom: '1.5rem' }}>
              Are you sure you want to cancel Order #{selectedOrder?.order_id}?
              <br /><br />
              <strong>This request will be sent to admin for approval.</strong> You will be notified once the admin approves your cancellation request.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowCancelConfirm(false);
                  setSelectedOrder(null);
                }}
                disabled={cancelLoading}
                style={{
                  background: '#6b7280',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.75rem 1.5rem',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                No, Keep Order
              </button>
              <button
                onClick={handleCancelConfirm}
                disabled={cancelLoading}
                style={{
                  background: '#dc2626',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.75rem 1.5rem',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: cancelLoading ? 'not-allowed' : 'pointer',
                  opacity: cancelLoading ? 0.6 : 1,
                  transition: 'all 0.3s ease'
                }}
              >
                {cancelLoading ? 'Requesting...' : 'Yes, Cancel Order'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
