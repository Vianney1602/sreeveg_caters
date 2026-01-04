import React, { useState, useEffect } from 'react';
import axios from 'axios';
import socketService from './services/socketService';
import './admin-dashboard.css';

export default function AdminDashboard({ onLogout }) {
  const normalizeName = (name = '') => String(name).trim().toLowerCase();
  // helper to convert status to a safe classname (no spaces)
  const statusToClass = (s = '') => String(s).toLowerCase().replace(/\s+/g, '-');
  const apiBase = (axios && axios.defaults && axios.defaults.baseURL) || '';

  const resolveImageUrl = (url) => {
    if (!url) return '';
    const trimmed = String(url).trim();
    
    // If it's a data URL or absolute URL, return as-is
    if (/^(data:|https?:)/i.test(trimmed)) return trimmed;
    
    // Get backend base URL - use axios defaults or environment
    const backendBase = (axios.defaults && axios.defaults.baseURL) || 
                       process.env.REACT_APP_API_URL || 
                       'http://127.0.0.1:5000';

    const toBackendUrl = (path) => {
      const clean = path.replace(/^\/+/, '');
      return `${backendBase}/${clean}`;
    };
    
    // If it starts with /static, static, /uploads or uploads, treat as backend asset
    if (
      trimmed.startsWith('/static') ||
      trimmed.startsWith('static') ||
      trimmed.startsWith('/uploads') ||
      trimmed.startsWith('uploads') ||
      trimmed.includes('/static/') ||
      trimmed.includes('/uploads/')
    ) {
      return toBackendUrl(trimmed);
    }
    
    // If it starts with /api, it's a backend URL
    if (trimmed.startsWith('/api')) {
      // Remove any leading duplicates
      const cleanPath = trimmed.replace(/^\/+/, '/');
      return `${backendBase}${cleanPath}`;
    }
    
    // If it starts with /images, it's a frontend public image
    if (trimmed.startsWith('/images')) {
      const base = process.env.PUBLIC_URL || '';
      return `${base}${trimmed}`;
    }
    
    // Bare filename? assume in public/images
    if (!trimmed.includes('/') && !trimmed.startsWith('.')) {
      const base = process.env.PUBLIC_URL || '';
      return `${base}/images/${trimmed}`;
    }
    
    // Fallback: assume backend-relative path
    return toBackendUrl(trimmed);
  };

  const suggestImageByName = (name) => {
    if (!name) return '';
    const n = name.toLowerCase();
    const base = (process.env.PUBLIC_URL || '');
    const img = (p) => `${base}/images/${p}`;
    if (n.includes('paneer') || n.includes('panner')) return img('paneer-tikka.jpg');
    if ((n.includes('butter') && (n.includes('paneer') || n.includes('panner'))) || n.includes('masala')) return img('panner_butter_masala.png');
    if (n.includes('parotta') || n.includes('paratha')) return img('parotta.jpg');
    if (n.includes('biryani') || n.includes('biriyani')) return img('veg-biriyani.jpg');
    if (n.includes('meals')) return img('veg-meals.jpeg');
    if (n.includes('gulab')) return img('gulab-jamun.jpg');
    if (n.includes('rasmalai') || n.includes('rasamalai')) return img('rasamalai.webp');
    if (n.includes('chola') || n.includes('chole') || n.includes('puri')) return img('chola_puri.png');
    if (n.includes('dal') || n.includes('dhal') || n.includes('makhani') || n.includes('makini')) return img('dhal_makini.png');
    if (n.includes('fish')) return img('fish_curry.png');
    if (n.includes('mutton')) return img('mutton_curry.png');
    if (n.includes('cutlet')) return img('veg-cutlet.webp');
    return img('chef.png');
  };

  const [activeTab, setActiveTab] = useState('overview');
  const [menuItems, setMenuItems] = useState([]);
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);
  const [adminInfo, setAdminInfo] = useState(null);
  const [stats, setStats] = useState({
    totalOrders: 0,
    pending: 0,
    revenue: '₹0',
    activeItems: 0,
    customers: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [showAddForm, setShowAddForm] = useState(false);
  const [newItem, setNewItem] = useState({
    name: '',
    categories: ['Morning Tiffin Menu'],
    price: '',
    description: '',
    image: '',
  });

  // NEW: edit state
  const [editingItem, setEditingItem] = useState(null);
  const [editForm, setEditForm] = useState({
    name: '',
    categories: ['Morning Tiffin Menu'],
    price: '',
    description: '',
    image: '',
  });

  // Image file selection for add/edit
  const [newImageFile, setNewImageFile] = useState(null);
  const [editImageFile, setEditImageFile] = useState(null);

  const [expandedOrderId, setExpandedOrderId] = useState(null);

  // Filter and sort states
  const [orderSortBy, setOrderSortBy] = useState('date-desc'); // 'date-desc', 'date-asc', 'name-asc', 'name-desc'
  const [customerSortBy, setCustomerSortBy] = useState('date-desc'); // 'date-desc', 'date-asc', 'name-asc', 'name-desc'
  const [customerFilterName, setCustomerFilterName] = useState(''); // Filter by name

  // Toast notification state
  const [toast, setToast] = useState(null);

  // Toast helper function
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000); // Auto-hide after 4 seconds
  };

  // Confirmation modal state
  const [confirmModal, setConfirmModal] = useState(null);

  // Fetch data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get token from sessionStorage
        const token = sessionStorage.getItem('_st');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        // Ensure socket connection uses the admin token
        socketService.connect(token);
        
        // Verify admin token first
        const verifyRes = await axios.get('/api/admin/verify', { headers });
        setAdminInfo(verifyRes.data.admin);

        // Fetch all required data in parallel
        const [ordersRes, menuRes, customersRes, statsRes, eventsRes] = await Promise.all([
          axios.get('/api/orders', { headers }),
          axios.get('/api/menu', { headers }),
          axios.get('/api/customers', { headers }),
          axios.get('/api/admin/stats', { headers }),
          axios.get('/api/events', { headers }),
        ]);

        // Process and set orders
        setOrders(ordersRes.data.map(order => ({
          id: order.order_id,
          orderId: order.order_id.toString(),
          customerName: order.customer_name,
          phone: order.phone_number,
          total: order.total_amount,
          totalLabel: `₹${order.total_amount}`,
          status: order.status,
          timestamp: order.created_at ? new Date(order.created_at).toLocaleString() : 'N/A',
          address: order.venue_address,
          eventDate: order.event_date,
          items: order.items && order.items.map(item => ({
            name: item.item_name,
            qty: item.quantity,
            price: item.price_at_order_time
          })) || []
        })));

        // Process and set menu items
        setMenuItems(menuRes.data.map(item => ({
          id: item.item_id,
          name: item.item_name,
          category: item.category,
          price: item.price_per_plate,
          description: item.description || '',
          available: item.is_available,
          imageUrl: resolveImageUrl(item.image_url)
        })));

        // Set customers
        setCustomers(customersRes.data);

        // Set event types - map response to correct format
        setEventTypes(eventsRes.data.map(event => ({
          event_type_id: event.id || event.event_type_id,
          event_name: event.name || event.event_name
        })));

        // Set stats
        setStats({
          totalOrders: statsRes.data.total_orders || 0,
          pending: statsRes.data.pending || 0,
          revenue: `₹${statsRes.data.revenue || 0}`,
          activeItems: menuRes.data.length,
          customers: customersRes.data.length,
        });

        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard. Please try logging in again.');
        setLoading(false);
        // Auto-logout on auth error
        if (err.response?.status === 401) {
          setTimeout(onLogout, 1500);
        }
      }
    };

    fetchData();

    // Listen for real-time order status changes
    const onOrderStatusChanged = (data) => {
      // Update the orders list with new status
      setOrders(prevOrders =>
        prevOrders.map(order =>
          order.id === data.order_id
            ? { ...order, status: data.new_status }
            : order
        )
      );

      if (Notification.permission === 'granted') {
        new Notification('Order Status Update', {
          body: `Order #${data.order_id} status changed to ${data.new_status}`,
          icon: '/images/chef.png'
        });
      }
    };

    const onCustomerCreated = (data) => {
      setCustomers((prev) => {
        if (!prev) return [data];
        const exists = prev.some(c => c.customer_id === data.customer_id);
        if (exists) return prev;
        return [data, ...prev];
      });

      setStats((prev) => ({
        ...prev,
        customers: (prev?.customers || 0) + 1,
      }));
    };

    socketService.on('order_status_changed', onOrderStatusChanged);
    socketService.on('customer_created', onCustomerCreated);

    // Listen for new orders in real-time
    const onOrderCreated = (data) => {
      setOrders(prev => {
        const exists = prev.some(o => o.id === data.order_id);
        if (exists) return prev;
        const newOrder = {
          id: data.order_id,
          orderId: data.order_id?.toString(),
          customerName: data.customer_name,
          phone: data.phone_number,
          total: data.total_amount,
          totalLabel: `₹${data.total_amount ?? 0}`,
          status: data.status,
          timestamp: data.created_at ? new Date(data.created_at).toLocaleString() : 'N/A',
          address: data.venue_address,
          eventDate: data.event_date,
          items: data.items || []
        };
        return [newOrder, ...prev];
      });

      // Optimistically bump stats
      setStats(prev => ({
        ...prev,
        totalOrders: (prev.totalOrders || 0) + 1,
        pending: (prev.pending || 0) + 1
      }));

      if (Notification.permission === 'granted') {
        new Notification('New Order Received', {
          body: `Order #${data.order_id} placed by ${data.customer_name || 'Customer'}`,
          icon: '/images/chef.png'
        });
      }
    };

    socketService.on('order_created', onOrderCreated);

    // Cleanup listener when component unmounts
    return () => {
      socketService.off('order_status_changed', onOrderStatusChanged);
      socketService.off('customer_created', onCustomerCreated);
      socketService.off('order_created', onOrderCreated);
    };
  }, [onLogout]);

  const handleAddItem = async (e) => {
    e.preventDefault();

    const formData = editingItem ? editForm : newItem;
    const selectedCategories = formData.categories || [];

    if (!formData.name || !formData.price) {
      showToast('Please fill in all required fields: Name and Price', 'error');
      return;
    }

    if (selectedCategories.length === 0) {
      showToast('Please select at least one category', 'error');
      return;
    }

    try {
      // Get token from sessionStorage
      const token = sessionStorage.getItem('_st');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      // If a file is selected, upload it first
      let imageUrl = formData.image || '';
      const fileToUpload = editingItem ? editImageFile : newImageFile;
      
      if (fileToUpload) {
        const fd = new FormData();
        fd.append('image', fileToUpload);
        try {
          const upRes = await axios.post('/api/uploads/image', fd, {
            headers: { ...headers, 'Content-Type': 'multipart/form-data' },
          });
          imageUrl = (upRes && upRes.data && upRes.data.url) || imageUrl;
        } catch (uploadErr) {
          console.error('Image upload failed:', uploadErr);
          showToast('Image upload failed. Item will be saved without image.', 'error');
        }
      }

      if (editingItem) {
        // For editing: find all existing items with this name
        const existingItems = menuItems.filter((it) =>
          normalizeName(it.name) === normalizeName(formData.name)
        );

        // Update payload
        const updatePayload = {
          item_name: formData.name,
          price: parseInt(formData.price, 10),
          description: formData.description,
          veg: true,
          is_available: true,
        };
        
        if (imageUrl) {
          updatePayload.image = imageUrl;
        }

        // Update or create items for each selected category
        for (const category of selectedCategories) {
          const existing = existingItems.find(it => it.category === category);
          
          if (existing) {
            // Update existing item
            await axios.put(`/api/menu/${existing.id}`, { ...updatePayload, category }, { headers });
          } else {
            // Create new item in this category
            await axios.post('/api/menu', { ...updatePayload, category }, { headers });
          }
        }

        // Delete items from categories that are no longer selected
        const categoriesToRemove = existingItems.filter(
          it => !selectedCategories.includes(it.category)
        );
        
        for (const item of categoriesToRemove) {
          await axios.delete(`/api/menu/${item.id}`, { headers });
        }

        showToast(`"${formData.name}" has been updated successfully! ✓`, 'success');
      } else {
        // Add new item to all selected categories
        const addPayload = {
          item_name: formData.name,
          price: parseInt(formData.price, 10),
          description: formData.description,
          veg: true,
        };
        
        if (imageUrl) {
          addPayload.image = imageUrl;
        }
        
        // Create item in each selected category
        for (const category of selectedCategories) {
          await axios.post('/api/menu', { ...addPayload, category }, { headers });
        }
        
        showToast(`"${formData.name}" has been added to the menu! ✓`, 'success');
      }

      // Refresh menu items
      const res = await axios.get('/api/menu', { headers });
      const updatedItems = res.data.map(item => ({
        id: item.item_id,
        name: item.item_name,
        category: item.category,
        price: item.price_per_plate,
        description: item.description || '',
        available: item.is_available,
        imageUrl: resolveImageUrl(item.image_url)
      }));
      
      // Ensure no duplicates by filtering unique IDs
      const uniqueItems = updatedItems.filter((item, index, self) =>
        index === self.findIndex((t) => t.id === item.id)
      );
      
      setMenuItems(uniqueItems);

      // Reset forms and close
      cancelEditing();
    } catch (err) {
      console.error('Error saving item:', err);
      showToast(`Failed to save item: ${err.response?.data?.message || err.message}`, 'error');
    }
  };

  const toggleItemAvailability = (id) => {
    const item = menuItems.find(it => it.id === id);
    if (!item) return;

    const targetStatus = !item.available;
    // Find all items with the same name (across all categories)
    const linkedItems = menuItems.filter((it) =>
      normalizeName(it.name) === normalizeName(item.name)
    );

    const token = sessionStorage.getItem('_st');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    Promise.all(
      linkedItems.map((it) =>
        axios.put(`/api/menu/${it.id}`, { is_available: targetStatus }, { headers })
      )
    )
      .then(() => {
        const newStatus = targetStatus ? 'Available' : 'Unavailable';
        setMenuItems(menuItems.map(it =>
          linkedItems.some(r => r.id === it.id)
            ? { ...it, available: targetStatus }
            : it
        ));
        const scopeMsg = newStatus === 'Available'
          ? 'Item will appear on all customer menus.'
          : 'Item is hidden from all customer menus.';
        showToast(`"${item.name}" is now ${newStatus}. ${scopeMsg}`, 'success');
      })
      .catch(err => {
        console.error('Error updating item availability:', err);
        showToast(`Failed to update item availability: ${err.response?.data?.message || err.message}`, 'error');
      });
  };

  const deleteItem = (id) => {
    const item = menuItems.find(it => it.id === id);
    if (!item) return;

    // Show custom confirmation modal
    setConfirmModal({
      title: 'Delete Menu Item',
      message: `Are you sure you want to delete "${item.name}"? This action cannot be undone.`,
      onConfirm: () => {
        setConfirmModal(null);
        const token = sessionStorage.getItem('_st');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        axios.delete(`/api/menu/${id}`, { headers })
          .then(() => {
            setMenuItems(menuItems.filter(item => item.id !== id));
            if (editingItem && editingItem === id) {
              cancelEditing();
            }
            showToast(`"${item.name}" has been deleted successfully! ✓`, 'success');
          })
          .catch(err => {
            console.error('Error deleting item:', err);
            showToast(`Failed to delete item: ${err.response?.data?.message || err.message}`, 'error');
          });
      },
      onCancel: () => setConfirmModal(null)
    });
  };

  const startEditingItem = (item) => {
    setEditingItem(item.id);
    
    // Find all categories this item exists in (by matching name)
    const allCategoriesForItem = menuItems
      .filter((it) => normalizeName(it.name) === normalizeName(item.name))
      .map(it => it.category);
    
    // Remove duplicates
    const uniqueCategories = [...new Set(allCategoriesForItem)];
    
    setEditForm({
      name: item.name,
      categories: uniqueCategories,
      price: item.price.toString(),
      description: item.description,
      image: item.imageUrl || '',
    });
    setEditImageFile(null);
    setShowAddForm(true);
  };

  const cancelEditing = () => {
    setShowAddForm(false);
    setEditingItem(null);
    setEditForm({ name: '', categories: ['Morning Tiffin Menu'], price: '', description: '', image: '' });
    setEditImageFile(null);
    setNewItem({ name: '', categories: ['Morning Tiffin Menu'], price: '', description: '', image: '' });
    setNewImageFile(null);
  };

  const toggleOrderDetails = (id) => {
    setExpandedOrderId(expandedOrderId === id ? null : id);
  };

  // Sorting function for orders
  const getSortedOrders = () => {
    const sorted = [...orders];
    switch (orderSortBy) {
      case 'date-desc':
        return sorted.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      case 'date-asc':
        return sorted.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      case 'name-asc':
        return sorted.sort((a, b) => a.customerName.localeCompare(b.customerName));
      case 'name-desc':
        return sorted.sort((a, b) => b.customerName.localeCompare(a.customerName));
      default:
        return sorted;
    }
  };

  // Sorting and filtering function for customers
  const getFilteredAndSortedCustomers = () => {
    let filtered = customers;
    
    // Filter by name
    if (customerFilterName.trim()) {
      filtered = filtered.filter(c =>
        c.full_name.toLowerCase().includes(customerFilterName.toLowerCase()) ||
        c.email.toLowerCase().includes(customerFilterName.toLowerCase())
      );
    }

    // Sort
    const sorted = [...filtered];
    switch (customerSortBy) {
      case 'date-desc':
        return sorted.sort((a, b) => new Date(b.customer_id) - new Date(a.customer_id));
      case 'date-asc':
        return sorted.sort((a, b) => new Date(a.customer_id) - new Date(b.customer_id));
      case 'name-asc':
        return sorted.sort((a, b) => a.full_name.localeCompare(b.full_name));
      case 'name-desc':
        return sorted.sort((a, b) => b.full_name.localeCompare(a.full_name));
      default:
        return sorted;
    }
  };

  const updateOrderStatus = (id, newStatus) => {
    const token = sessionStorage.getItem('_st');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    axios.put(`/api/orders/status/${id}`, { status: newStatus }, { headers })
      .then((response) => {
        setOrders(orders.map(order =>
          order.id === id ? { ...order, status: newStatus } : order
        ));
      })
      .catch(err => {
        alert('Failed to update order status');
      });
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="error">{error}</div>
        <button onClick={onLogout} className="logout-btn">Logout</button>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      {/* Header */}
      <div className="admin-header">
        <div className="admin-header-left">
          <h1 className="admin-logo">🍽️ Hotel Shanmuga Bhavaan</h1>
          <span className="admin-badge">Admin</span>
        </div>
        <div className="admin-header-right">
          <span className="admin-email">{adminInfo?.email || 'admin@shanmugabhavaan.com'}</span>
          <button onClick={onLogout} className="logout-btn">→ Logout</button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'menu' ? 'active' : ''}`}
          onClick={() => setActiveTab('menu')}
        >
          🍽️ Menu Management
        </button>
        <button
          className={`tab-btn ${activeTab === 'orders' ? 'active' : ''}`}
          onClick={() => setActiveTab('orders')}
        >
          📋 Orders
        </button>
        <button
          className={`tab-btn ${activeTab === 'customers' ? 'active' : ''}`}
          onClick={() => setActiveTab('customers')}
        >
          👥 Customers
        </button>
        <button
          className={`tab-btn ${activeTab === 'database' ? 'active' : ''}`}
          onClick={() => setActiveTab('database')}
        >
          🗄️ Database
        </button>
      </div>

      {/* Content */}
      <div className="admin-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Stats Grid */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📦</div>
                <div className="stat-info">
                  <div className="stat-label">Total Orders</div>
                  <div className="stat-value">{stats.totalOrders}</div>
                  <div className="stat-subtitle">📈 {stats.pending} pending</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">💰</div>
                <div className="stat-info">
                  <div className="stat-label">Revenue</div>
                  <div className="stat-value">{stats.revenue}</div>
                  <div className="stat-subtitle">📈 All time</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🍽️</div>
                <div className="stat-info">
                  <div className="stat-label">Active Items</div>
                  <div className="stat-value">{stats.activeItems}</div>
                  <div className="stat-subtitle">📈 of {stats.activeItems} total</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">👥</div>
                <div className="stat-info">
                  <div className="stat-label">Customers</div>
                  <div className="stat-value">{stats.customers}</div>
                  <div className="stat-subtitle">📈 Unique</div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button onClick={() => setActiveTab('menu')} className="action-btn primary">
                  🍽️ Manage Menu
                </button>
                <button onClick={() => setActiveTab('orders')} className="action-btn secondary">
                  📋 View Orders
                </button>
              </div>
            </div>

            {/* Recent Orders */}
            <div className="recent-section">
              <div className="section-header">
                <h3>Recent Orders</h3>
                <button className="view-all">View All</button>
              </div>
              <div className="orders-list">
                {orders.map(order => (
                  <div
                    key={order.id}
                    className="order-row"
                    onClick={() => toggleOrderDetails(order.id)}
                    role="button"
                    tabIndex={0}
                  >
                    <div>
                      <div className="order-name">{order.customerName}</div>
                      <div className="order-phone">{order.phone}</div>
                    </div>
                    <div className="order-total">₹{order.total}</div>
                    <div className="order-status">{order.status}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Menu Management Tab */}
        {activeTab === 'menu' && (
          <>
            <div className="menu-header-admin">
              <h3>Menu Items ({menuItems.length})</h3>
              <button
                onClick={() => {
                  setShowAddForm(true);
                  setEditingItem(null); // reset to add mode
                  setNewItem({ name: '', categories: ['Morning Tiffin Menu'], price: '', description: '', image: '' });
                  setEditForm({ name: '', categories: ['Morning Tiffin Menu'], price: '', description: '', image: '' });
                  setNewImageFile(null);
                  setEditImageFile(null);
                }}
                className="add-item-btn"
              >
                + Add Item
              </button>
            </div>

            {/* Add / Edit Item Form */}
            {showAddForm && (
              <div className="add-form-container">
                <form onSubmit={handleAddItem} className="add-item-form">
                  <input
                    type="text"
                    placeholder="Item Name"
                    value={editingItem ? editForm.name : newItem.name}
                    onChange={(e) =>
                      editingItem
                        ? setEditForm((prev) => {
                            const name = e.target.value;
                            return {
                              ...prev,
                              name,
                              image: prev.image || suggestImageByName(name),
                            };
                          })
                        : setNewItem((prev) => {
                            const name = e.target.value;
                            return {
                              ...prev,
                              name,
                              image: prev.image || suggestImageByName(name),
                            };
                          })
                    }
                    required
                  />
                  <select
                    multiple
                    value={editingItem ? editForm.categories : newItem.categories}
                    onChange={(e) => {
                      const selected = Array.from(e.target.selectedOptions, option => option.value);
                      if (selected.length === 0) return; // Prevent empty selection
                      editingItem
                        ? setEditForm({ ...editForm, categories: selected })
                        : setNewItem({ ...newItem, categories: selected });
                    }}
                    style={{ minHeight: '80px' }}
                  >
                    <option value="Morning Tiffin Menu">Morning Tiffin Menu</option>
                    <option value="Lunch Menu">Lunch Menu</option>
                    <option value="Dinner Menu">Dinner Menu</option>
                  </select>
                  <div style={{ fontSize: '0.85em', color: '#666', marginTop: '-8px', marginBottom: '8px' }}>
                    Hold Ctrl (Windows) or Cmd (Mac) to select multiple categories
                  </div>
                  <input
                    type="number"
                    placeholder="Price"
                    value={editingItem ? editForm.price : newItem.price}
                    onChange={(e) =>
                      editingItem
                        ? setEditForm({ ...editForm, price: e.target.value })
                        : setNewItem({ ...newItem, price: e.target.value })
                    }
                    required
                  />
                  <textarea
                    placeholder="Description"
                    value={editingItem ? editForm.description : newItem.description}
                    onChange={(e) =>
                      editingItem
                        ? setEditForm({ ...editForm, description: e.target.value })
                        : setNewItem({ ...newItem, description: e.target.value })
                    }
                  />
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files && e.target.files[0];
                      if (editingItem) {
                        setEditImageFile(file || null);
                        if (file) setEditForm({ ...editForm, image: '' });
                      } else {
                        setNewImageFile(file || null);
                        if (file) setNewItem({ ...newItem, image: '' });
                      }
                    }}
                  />
                  <div className="image-preview">
                    <span>Preview:</span>
                    <img
                      src={editingItem
                        ? (editImageFile 
                            ? URL.createObjectURL(editImageFile) 
                            : (editForm.image || suggestImageByName(editForm.name)))
                        : (newImageFile 
                            ? URL.createObjectURL(newImageFile) 
                            : (newItem.image || suggestImageByName(newItem.name)))}
                      alt="preview"
                      onError={(e) => {
                        e.currentTarget.onerror = null;
                        e.currentTarget.src = `${process.env.PUBLIC_URL || ''}/images/chef.png`;
                      }}
                    />
                  </div>
                  <div className="form-actions">
                    <button type="submit" className="save-btn">
                      {editingItem ? 'Update Item' : 'Save Item'}
                    </button>
                    <button
                      type="button"
                      onClick={cancelEditing}
                      className="cancel-btn"
                    >
                      Cancel
                    </button>
                    {editingItem && (
                      <button
                        type="button"
                        onClick={() => deleteItem(editingItem)}
                        className="delete-btn-form"
                      >
                        🗑️ Delete Item
                      </button>
                    )}
                  </div>
                </form>
              </div>
            )}

            {/* Menu Items List */}
            <div className="menu-list">
              {menuItems.map(item => (
                <div key={item.id} className="menu-item-row">
                  <div className="item-image">
                    {item.imageUrl ? (
                      <img
                        src={item.imageUrl}
                        alt={item.name}
                        className="menu-thumb"
                        onError={(e) => {
                          e.currentTarget.onerror = null;
                          e.currentTarget.src = `${process.env.PUBLIC_URL || ''}/images/chef.png`;
                        }}
                      />
                    ) : (
                      <span role="img" aria-label="dish">🍽️</span>
                    )}
                  </div>
                  <div className="item-details">
                    <div className="item-name">{item.name}</div>
                    <div className="item-category">{item.category}</div>
                    <div className="item-desc">{item.description}</div>
                  </div>
                  <div className="item-price">₹{item.price}</div>
                  <div className="item-actions">
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={item.available}
                        onChange={() => toggleItemAvailability(item.id)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                    <button
                      className="edit-btn"
                      type="button"
                      title="Edit item"
                      onClick={() => startEditingItem(item)}
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="delete-btn"
                      type="button"
                      title="Delete item"
                      style={{ display: 'inline-block', visibility: 'visible' }}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Orders Tab with expandable details */}
        {activeTab === 'orders' && (
          <div className="orders-section">
            <div className="orders-header">
              <h3>All Orders ({orders.length})</h3>
              <div className="sort-controls">
                <label htmlFor="order-sort">Sort by:</label>
                <select 
                  id="order-sort"
                  value={orderSortBy} 
                  onChange={(e) => setOrderSortBy(e.target.value)}
                  className="sort-select"
                >
                  <option value="date-desc">📅 Newest First</option>
                  <option value="date-asc">📅 Oldest First</option>
                  <option value="name-asc">👤 Customer A-Z</option>
                  <option value="name-desc">👤 Customer Z-A</option>
                </select>
              </div>
            </div>
            <div className="orders-table">
              {getSortedOrders().map(order => (
                <div key={order.id} className="order-card">
                  <div className="order-card-header">
                    <div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <strong>{order.orderId}</strong>
                        <span className={`status-badge ${statusToClass(order.status)}`}>{order.status}</span>
                      </div>
                      <div className="order-meta">{order.customerName} • {order.phone}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="order-total-amount">₹{order.total}</div>
                      <div className="order-time">{order.timestamp}</div>
                      <button
                        className="expand-btn"
                        onClick={() => toggleOrderDetails(order.id)}
                      >
                        {expandedOrderId === order.id ? '▴' : '▾'}
                      </button>
                    </div>
                  </div>

                  {expandedOrderId === order.id && (
                    <div className="order-card-body order-details-grid">
                      <div className="order-items">
                        <h4>Order Items</h4>
                        <div className="items-list">
                          {order.items.map((it, idx) => (
                            <div key={idx} className="order-item-row">
                              <div className="item-name-col">{it.name} × {it.qty}</div>
                              <div className="item-price-col">₹{it.price}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="order-right">
                        <h4>Delivery Address</h4>
                        <p className="delivery-address">{order.address}</p>

                        <h4 style={{ marginTop: '1rem' }}>Event Date</h4>
                        <p>{order.eventDate}</p>

                        <div className="update-status-section">
                          <h4>Update Status</h4>
                          <div className="status-buttons">
                            {['Pending', 'Paid', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled'].map(s => (
                              <button
                                key={s}
                                className={`status-btn ${order.status === s ? 'active' : ''}`}
                                onClick={() => updateOrderStatus(order.id, s)}
                                type="button"
                              >
                                {s}
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Customers Tab */}
        {activeTab === 'customers' && (
          <div className="customers-section">
            <div className="customers-header">
              <h3>All Customers ({customers.length})</h3>
              <div className="filter-sort-controls">
                <input
                  type="text"
                  placeholder="🔍 Search by name or email..."
                  value={customerFilterName}
                  onChange={(e) => setCustomerFilterName(e.target.value)}
                  className="search-input"
                />
                <select 
                  value={customerSortBy} 
                  onChange={(e) => setCustomerSortBy(e.target.value)}
                  className="sort-select"
                >
                  <option value="date-desc">📅 Newest First</option>
                  <option value="date-asc">📅 Oldest First</option>
                  <option value="name-asc">👤 Name A-Z</option>
                  <option value="name-desc">👤 Name Z-A</option>
                </select>
              </div>
            </div>
            <div className="customers-table">
              <div className="table-header">
                <div className="table-cell">Customer ID</div>
                <div className="table-cell">Name</div>
                <div className="table-cell">Email</div>
                <div className="table-cell">Phone</div>
                <div className="table-cell">Total Orders</div>
              </div>
              {getFilteredAndSortedCustomers().length > 0 ? (
                getFilteredAndSortedCustomers().map(customer => (
                  <div key={customer.customer_id} className="table-row">
                    <div className="table-cell">#{customer.customer_id}</div>
                    <div className="table-cell">{customer.full_name}</div>
                    <div className="table-cell">{customer.email}</div>
                    <div className="table-cell">{customer.phone_number}</div>
                    <div className="table-cell">{customer.total_orders_count || 0}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>No customers found matching your search.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Database Tab */}
        {activeTab === 'database' && (
          <div className="database-section">
            <h3>Database Overview</h3>
            
            <div className="database-grid">
              {/* Orders Table */}
              <div className="db-table-card">
                <h4>📋 Orders Table</h4>
                <p className="db-count">{orders.length} records</p>
                <div className="db-details">
                  <div className="db-stat">
                    <span>Pending:</span>
                    <strong>{orders.filter(o => o.status === 'Pending').length}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Paid:</span>
                    <strong>{orders.filter(o => o.status === 'Paid').length}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Delivered:</span>
                    <strong>{orders.filter(o => o.status === 'Delivered').length}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Cancelled:</span>
                    <strong>{orders.filter(o => o.status === 'Cancelled').length}</strong>
                  </div>
                </div>
              </div>

              {/* Menu Items Table */}
              <div className="db-table-card">
                <h4>🍽️ Menu Items Table</h4>
                <p className="db-count">{menuItems.length} records</p>
                <div className="db-details">
                  <div className="db-stat">
                    <span>Available:</span>
                    <strong>{menuItems.filter(m => m.available).length}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Unavailable:</span>
                    <strong>{menuItems.filter(m => !m.available).length}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Categories:</span>
                    <strong>{[...new Set(menuItems.map(m => m.category))].length}</strong>
                  </div>
                </div>
              </div>

              {/* Customers Table */}
              <div className="db-table-card">
                <h4>👥 Customers Table</h4>
                <p className="db-count">{customers.length} records</p>
                <div className="db-details">
                  <div className="db-stat">
                    <span>Registered:</span>
                    <strong>{customers.filter(c => c.password_hash).length}</strong>
                  </div>
                  <div className="db-stat">
                    <span>Guest:</span>
                    <strong>{customers.filter(c => !c.password_hash).length}</strong>
                  </div>
                </div>
              </div>

              {/* Event Types Table */}
              <div className="db-table-card">
                <h4>🎉 Event Types Table</h4>
                <p className="db-count">{eventTypes.length} records</p>
                <div className="db-details">
                  {eventTypes.map(event => (
                    <div key={event.event_type_id} className="db-stat">
                      <span>{event.event_name}:</span>
                      <strong>Active</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Database Activity */}
            <div className="recent-activity">
              <h4>Recent Activity</h4>
              <div className="activity-list">
                {orders.slice(0, 5).map(order => (
                  <div key={order.id} className="activity-item">
                    <span className="activity-icon">📝</span>
                    <span className="activity-text">
                      New order #{order.orderId} from {order.customerName}
                    </span>
                    <span className="activity-time">{order.timestamp}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* System Info */}
            <div className="system-info">
              <h4>System Information</h4>
              <div className="info-grid">
                <div className="info-item">
                  <span>Database Type:</span>
                  <strong>SQLite</strong>
                </div>
                <div className="info-item">
                  <span>Total Tables:</span>
                  <strong>8</strong>
                </div>
                <div className="info-item">
                  <span>Admin User:</span>
                  <strong>{adminInfo?.email}</strong>
                </div>
                <div className="info-item">
                  <span>Payment Methods:</span>
                  <strong>Razorpay, COD</strong>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Toast Notification */}
        {toast && (
          <div className={`toast-notification toast-${toast.type}`}>
            <div className="toast-content">
              {toast.type === 'success' && <span className="toast-icon">✓</span>}
              {toast.type === 'error' && <span className="toast-icon">✕</span>}
              <span className="toast-message">{toast.message}</span>
            </div>
          </div>
        )}

        {/* Confirmation Modal */}
        {confirmModal && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h3 className="modal-title">{confirmModal.title}</h3>
              <p className="modal-message">{confirmModal.message}</p>
              <div className="modal-actions">
                <button 
                  className="modal-btn modal-btn-confirm" 
                  onClick={confirmModal.onConfirm}
                >
                  Yes, Delete
                </button>
                <button 
                  className="modal-btn modal-btn-cancel" 
                  onClick={confirmModal.onCancel}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}