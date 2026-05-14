import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './admin.css';

export default function AccountPage({ customer, onLogout, goBack }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!customer) return;
    setLoading(true);
    axios.get(`/api/customers/${customer.customer_id}/orders`, { headers: { Authorization: `Bearer ${sessionStorage.getItem('_ct')}` } })
      .then(res => {
        setOrders(res.data || []);
        setLoading(false);
      })
      .catch(err => {
        setOrders([]);
        setLoading(false);
      });
  }, [customer]);

  return (
    <div className="admin-login-container">
      <div className="login-card">
        <div className="account-page-header-top">
          <button className="back-link" onClick={goBack}>← Back</button>
        </div>
        <div className="account-page-header">
          <div className="account-header-content">
            <div className="login-icon">🧾</div>
            <h1>My Account</h1>
            <p className="login-subtitle">{customer ? `Welcome, ${customer.full_name}` : 'Please sign in'}</p>
          </div>
          <button
            className="sign-in-btn account-logout-btn"
            onClick={() => {
              sessionStorage.removeItem('_ct');
              sessionStorage.removeItem('_cu');
              onLogout();
            }}
          >
            Logout
          </button>
        </div>

        <div style={{ textAlign: 'left' }}>

          <h3>Purchase History</h3>
          {loading && <div>Loading orders...</div>}
          {!loading && orders.length === 0 && <div>No orders yet.</div>}

          <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
            {orders.map(o => (
              <li key={o.order_id} style={{ borderBottom: '1px solid #eee', padding: '10px 0' }}>
                <div><strong>Order #{o.order_id}</strong> — ₹{o.total_amount}</div>
                <div>{o.date} {o.time} • {o.status}</div>
                <div>Event: {o.event} • Guests: {o.guests}</div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
