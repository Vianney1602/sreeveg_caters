import React, { useState, useEffect } from "react";
import axios from "axios";
import authService from "./services/authService";
import socketService from "./services/socketService";
import MenuPage from "./MenuPage";
import CartPage from "./CartPage";
import BulkMenuPage from "./BulkMenuPage";
import BulkCartPage from "./BulkCartPage";
import AdminLogin from "./AdminLogin";
import AdminDashboard from "./AdminDashboard";
import WelcomePage from "./WelcomePage";
import BulkOrderModal from "./BulkOrderModal";
import "./home.css";

function App() {
  // Check for existing session on mount
  const [initializing, setInitializing] = useState(true);
  
  // Event & Package State
  // eslint-disable-next-line no-unused-vars
  const [selectedEvent] = useState("");
  // eslint-disable-next-line no-unused-vars
  const [guestCount] = useState(50);
  // eslint-disable-next-line no-unused-vars
  const [selectedPackage] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [selectedDate] = useState("");
  // eslint-disable-next-line no-unused-vars
  const [selectedTime] = useState("");

  // UI Modals
  // eslint-disable-next-line no-unused-vars
  const [showBookingForm] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [showContact] = useState(false);
  const [showCart, setShowCart] = useState(false);
  const [showMenuPage, setShowMenuPage] = useState(false);
  const [showBulkMenu, setShowBulkMenu] = useState(false);
  const [showBulkCart, setShowBulkCart] = useState(false);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false); // Changed to false initially
  // removed customer account UI/state per request

  // Order type and guest count for bulk orders
  const [orderType, setOrderType] = useState("individual");
  const [bulkGuestCount, setBulkGuestCount] = useState(50);

  // Bulk order modal state
  const [showBulkOrderModal, setShowBulkOrderModal] = useState(false);
  const [selectedEventType, setSelectedEventType] = useState("");
  const [bulkOrderDetails, setBulkOrderDetails] = useState({});

  // Cart & Menu
  const [cart, setCart] = useState(() => {
    // Restore cart from sessionStorage on page load
    try {
      const savedCart = sessionStorage.getItem('_cart');
      return savedCart ? JSON.parse(savedCart) : {};
    } catch {
      return {};
    }
  });
  const [bulkCart, setBulkCart] = useState(() => {
    // Restore bulk cart from sessionStorage on page load
    try {
      const savedBulkCart = sessionStorage.getItem('_bulkCart');
      return savedBulkCart ? JSON.parse(savedBulkCart) : {};
    } catch {
      return {};
    }
  });
  // eslint-disable-next-line no-unused-vars
  const [selectedMenuItems, setSelectedMenuItems] = useState([]);
  const [, setEventTypes] = useState([]);
  const [, setMenuCategories] = useState([]);

  // Navigation helper functions
  const navigateToCart = () => {
    setShowMenuPage(false);
    setShowBulkMenu(false);
    setShowCart(true);
  };

  const navigateToMenu = () => {
    setShowCart(false);
    setShowBulkCart(false);
    setShowMenuPage(true);
  };

  const navigateToBulkCart = () => {
    setShowBulkMenu(false);
    setShowBulkCart(true);
  };

  const navigateToBulkMenu = () => {
    setShowBulkCart(false);
    setShowBulkMenu(true);
  };

  // Initialize WebSocket connection on app mount
  useEffect(() => {
    // Check for existing admin session
    const adminToken = sessionStorage.getItem('_st');
    if (adminToken) {
      // Verify token is still valid
      axios.get('/api/admin/verify', {
        headers: { Authorization: `Bearer ${adminToken}` }
      })
      .then(() => {
        setIsAdminLoggedIn(true);
        setShowWelcome(false);
      })
      .catch(() => {
        // Token invalid, clear it
        sessionStorage.removeItem('_st');
        sessionStorage.removeItem('_au');
      })
      .finally(() => {
        setInitializing(false);
      });
    } else {
      // Restore bulk guest count if exists
      const savedGuestCount = sessionStorage.getItem('_bulkGuestCount');
      if (savedGuestCount) {
        setBulkGuestCount(parseInt(savedGuestCount));
      }
      
      // Check for saved page state (for customer flow)
      const savedPage = sessionStorage.getItem('_currentPage');
      if (savedPage) {
        switch(savedPage) {
          case 'menu':
            setShowMenuPage(true);
            break;
          case 'cart':
            setShowCart(true);
            break;
          case 'bulkMenu':
            setShowBulkMenu(true);
            break;
          case 'bulkCart':
            setShowBulkCart(true);
            break;
          default:
            setShowWelcome(true);
        }
      } else {
        setShowWelcome(true);
      }
      setInitializing(false);
    }
    
    const token = sessionStorage.getItem('_ct'); // Customer token in sessionStorage
    socketService.connect(token);

    // Global debug: log any incoming socket events
    const onAny = (event, ...args) => {
      try {
        // Silent
      } catch (e) {
        // noop
      }
    };
    if (socketService.getSocket()) {
      socketService.getSocket().onAny(onAny);
    }

    // Explicitly listen for order status changes globally
    const onOrderStatus = (data) => {
      // Silent
    };
    socketService.on('order_status_changed', onOrderStatus);

    // Cleanup on unmount
    return () => {
      try {
        if (socketService.getSocket()) {
          socketService.getSocket().offAny(onAny);
        }
      } catch {}
      socketService.off('order_status_changed', onOrderStatus);
      socketService.disconnect();
    };
  }, []);
  
  // Save current page state to persist across reloads
  useEffect(() => {
    if (initializing) return; // Don't save during initialization
    
    if (showMenuPage) {
      sessionStorage.setItem('_currentPage', 'menu');
    } else if (showCart) {
      sessionStorage.setItem('_currentPage', 'cart');
    } else if (showBulkMenu) {
      sessionStorage.setItem('_currentPage', 'bulkMenu');
    } else if (showBulkCart) {
      sessionStorage.setItem('_currentPage', 'bulkCart');
    } else if (showWelcome) {
      sessionStorage.removeItem('_currentPage');
    }
  }, [showMenuPage, showCart, showBulkMenu, showBulkCart, showWelcome, initializing]);
  
  // Persist cart state
  useEffect(() => {
    if (initializing) return;
    sessionStorage.setItem('_cart', JSON.stringify(cart));
  }, [cart, initializing]);
  
  // Persist bulk cart state
  useEffect(() => {
    if (initializing) return;
    sessionStorage.setItem('_bulkCart', JSON.stringify(bulkCart));
  }, [bulkCart, initializing]);
  
  // Save bulk guest count
  useEffect(() => {
    if (initializing) return;
    sessionStorage.setItem('_bulkGuestCount', bulkGuestCount.toString());
  }, [bulkGuestCount, initializing]);
  
  const [paymentStatus, setPaymentStatus] = useState(null); // For payment feedback
  // Dashboard Stats (if needed)
  const [dashboardStats, setDashboardStats] = useState({});

  // Axios default config - supports both dev and production
  const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";
  axios.defaults.baseURL = API_BASE_URL;
  axios.defaults.headers.post["Content-Type"] = "application/json";

  // Payment function using Razorpay
  const initiatePayment = (orderId, amount, customerDetails, onSuccess, onError) => {
    const options = {
      key: process.env.REACT_APP_RAZORPAY_KEY || 'rzp_live_YOUR_PRODUCTION_KEY',
      amount: amount * 100, // Amount in paisa
      currency: 'INR',
      name: 'Hotel Shanmuga Bhavaan',
      description: 'Order Payment',
      order_id: orderId, // Razorpay order ID from backend
      handler: function (response) {
        // Handle successful payment
        axios.post('/api/payments/verify', {
          payment_id: response.razorpay_payment_id,
          order_id: orderId,
          razorpay_order_id: response.razorpay_order_id,
          razorpay_signature: response.razorpay_signature
        }).then(() => {
          setPaymentStatus({
            type: 'success',
            message: 'Payment successful! Order confirmed.',
            orderId: orderId
          });
          // Auto-hide after 5 seconds
          setTimeout(() => setPaymentStatus(null), 5000);
          if (onSuccess) onSuccess();
        }).catch(err => {
          setPaymentStatus({
            type: 'error',
            message: 'Payment verification failed. Please contact support.'
          });
          // Auto-hide after 5 seconds
          setTimeout(() => setPaymentStatus(null), 5000);
          if (onError) onError(err);
        });
      },
      modal: {
        ondismiss: function () {
          // User closed/cancelled the payment modal
          axios.post('/api/payments/cancel', { razorpay_order_id: orderId }).catch(() => {});
          setPaymentStatus({
            type: 'error',
            message: 'Payment cancelled. You can retry from the cart.'
          });
          setTimeout(() => setPaymentStatus(null), 5000);
          if (onError) onError(new Error('Payment cancelled'));
        }
      },
      prefill: {
        name: customerDetails?.name || "Hotel Shanmuga Bhavaan",
        email: customerDetails?.email || "",
        contact: customerDetails?.phone || ""
      },
      theme: {
        color: '#3399cc'
      }
    };
    const rzp = new window.Razorpay(options);
    rzp.open();
  };

  // Fetch event types and menu items from backend
  useEffect(() => {
    axios
      .get("/api/event_types")
      .then((res) => setEventTypes(res.data))
      .catch((err) => {
        // Silent error handling
      });

    axios
      .get("/api/menu_items")
      .then((res) => {
        const categories = {};
        res.data.forEach((item) => {
          if (!categories[item.category]) categories[item.category] = [];
          categories[item.category].push(item);
        });
        setMenuCategories(
          Object.keys(categories).map((key) => ({
            category: key,
            items: categories[key],
          }))
        );
      })
      .catch((err) => {
        // Silent error handling
      });
  }, []);

  // Cart functions
  const updateQty = (id, qty) => {
    setCart((prev) => {
      if (qty <= 0) {
        const updated = { ...prev };
        delete updated[id];
        return updated;
      }
      return { ...prev, [id]: { ...prev[id], qty } };
    });
  };

  const addToCart = (item) => {
    setCart((prev) => ({
      ...prev,
      [item.id]: {
        ...item,
        qty: (prev[item.id]?.qty || 0) + 1,
        price: item.price,
      },
    }));
  };

  // Bulk order modal handlers
  const handleEventClick = (eventType) => {
    setSelectedEventType(eventType);
    setShowBulkOrderModal(true);
  };

  const handleBulkOrderSubmit = (formData) => {
    setBulkOrderDetails(formData);
    setBulkGuestCount(parseInt(formData.numberOfPersons));
    setOrderType("bulk");
    setShowBulkOrderModal(false);
    setShowBulkMenu(true);
  };

  const handleBulkOrderModalClose = () => {
    setShowBulkOrderModal(false);
    setSelectedEventType("");
  };

  // const toggleMenuItem = (itemId) => {
  //   setSelectedMenuItems(prev =>
  //     prev.includes(itemId) ? prev.filter(id => id !== itemId) : [...prev, itemId]
  //   );
  // };

  // const calculateTotal = () => {
  //   if (!selectedPackage) return 0;
  //   const pkg = packages.find(p => p.id === selectedPackage);
  //   return pkg ? pkg.pricePerHead * guestCount : 0;
  // };

  // Booking form submission
  // const handleBookingSubmit = (e) => {
  //   e.preventDefault();
  //   const data = {
  //     customer_name: e.target[0].value,
  //     phone: e.target[1].value,
  //     email: e.target[2].value,
  //     event_type: selectedEvent,
  //     number_of_guests: guestCount,
  //     event_date: selectedDate,
  //     event_time: selectedTime,
  //     venue_address: e.target[6].value,
  //     special_requirements: e.target[7].value,
  //     selected_menu_items: selectedMenuItems,
  //     package: selectedPackage
  //   };

  //   axios.post('/api/orders', data)
  //     .then(res => {
  //       alert('Booking submitted successfully!');
  //       setShowBookingForm(false);
  //       setCart({});
  //       setSelectedMenuItems([]);
  //     })
  //     .catch(err => {
  //       console.error(err);
  //       alert('Error submitting booking.');
  //     });
  // };

  // Admin login
  const handleAdminLogin = (username, password) => {
    axios
      .post("/api/admin/login", { username, password })
      .then((res) => {
        // Store token in sessionStorage (cleared on browser close) instead of localStorage
        sessionStorage.setItem("_st", res.data.access_token);
        sessionStorage.setItem("_au", JSON.stringify({ username }));
        setShowAdminLogin(false);
        setIsAdminLoggedIn(true);
      })
      .catch((err) => {
        alert("Login failed!");
      });
  };

  // Dashboard stats fetch (optional)
  useEffect(() => {
    if (isAdminLoggedIn) {
      axios
        .get("/api/admin/stats")
        .then((res) => setDashboardStats(res.data))
        .catch(() => {});
    }
  }, [isAdminLoggedIn]);

  // Show loading while checking for existing session
  if (initializing) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '1.5rem',
        color: '#3399cc'
      }}>
        Loading...
      </div>
    );
  }

  // Conditional renders - Admin checks first (highest priority)
  if (isAdminLoggedIn) {
    return (
      <AdminDashboard
        onLogout={() => {
          authService.logout();
          setIsAdminLoggedIn(false);
          setShowWelcome(true);
          sessionStorage.removeItem('_currentPage'); // Clear saved page state
        }}
        stats={dashboardStats}
      />
    );
  }
  
  if (showAdminLogin) {
    return (
      <AdminLogin
        goBack={() => {
          setShowAdminLogin(false);
          setShowWelcome(true);
        }}
        onLoginSuccess={() => {
          // Reset all other UI states to ensure clean dashboard render
          setShowAdminLogin(false);
          setShowWelcome(false);
          setShowMenuPage(false);
          setShowCart(false);
          setShowBulkMenu(false);
          setShowBulkCart(false);
          setIsAdminLoggedIn(true);
        }}
      />
    );
  }
  
  if (showWelcome)
    return (
      <WelcomePage
        goUser={() => setShowWelcome(false)}
        goAdmin={() => {
          setShowWelcome(false);
          setShowAdminLogin(true);
        }}
      />
    );
  if (showCart)
    return (
      <CartPage
        goBack={navigateToMenu}
        cart={cart}
        updateQty={updateQty}
        clearCart={() => setCart({})}
        initiatePayment={initiatePayment}
        paymentStatus={paymentStatus}
        clearPaymentStatus={() => setPaymentStatus(null)}
      />
    );
  if (showMenuPage)
    return (
      <MenuPage
        goBack={() => {
          setShowMenuPage(false);
          setShowWelcome(true);
        }}
        goToCart={navigateToCart}
        cart={cart}
        updateQty={updateQty}
        addToCart={addToCart}
      />
    );
  if (showBulkMenu)
    return (
      <BulkMenuPage
        guestCount={bulkGuestCount}
        bulkCart={bulkCart}
        setBulkCart={setBulkCart}
        goToCart={navigateToBulkCart}
        goBack={() => {
          setShowBulkMenu(false);
          setShowWelcome(true);
        }}
      />
    );
  if (showBulkCart)
    return (
      <BulkCartPage
        guestCount={bulkGuestCount}
        bulkCart={bulkCart}
        setBulkCart={setBulkCart}
        goBack={navigateToBulkMenu}
        clearCart={() => setBulkCart({})}
        initiatePayment={initiatePayment}
        defaultPaymentMethod="online"
        paymentStatus={paymentStatus}
        clearPaymentStatus={() => setPaymentStatus(null)}
      />
    );

  // Packages hardcoded (can also fetch from backend if needed)
  const packages = [
    {
      id: "silver",
      name: "Silver Package",
      icon: "🥈",
      pricePerHead: 299,
      features: [
        "3 Main Courses",
        "2 Side Dishes",
        "1 Dessert",
        "Soft Drinks",
        "Basic Decoration",
      ],
    },
    {
      id: "gold",
      name: "Gold Package",
      icon: "🥇",
      pricePerHead: 499,
      features: [
        "5 Main Courses",
        "3 Side Dishes",
        "2 Desserts",
        "Welcome Drinks",
        "Premium Decoration",
        "Live Counter",
      ],
    },
    {
      id: "platinum",
      name: "Platinum Package",
      icon: "💎",
      pricePerHead: 799,
      features: [
        "7 Main Courses",
        "4 Side Dishes",
        "3 Desserts",
        "Welcome Drinks & Cocktails",
        "Luxury Decoration",
        "Multiple Live Counters",
        "Chef Service",
      ],
    },
  ];

  // Main return (UI intact)
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <h2 className="header-title">Hotel Shanmuga Bhavaan</h2>
            <div className="header-contact">
              <span className="header-phone">📞 79044 79451</span>
              <span className="header-email">📧 shanmugapriyaraja31@gmail.com</span>
            </div>
          </div>
          <nav className="header-nav" aria-label="Primary">
            <button onClick={() => setShowMenuPage(true)}>View Menu</button>
            <span className="nav-separator" aria-hidden="true">|</span>
            <button onClick={() => setShowCart(true)}>
              Cart ({Object.keys(cart).length})
            </button>
            <span className="nav-separator" aria-hidden="true">|</span>
            <button onClick={() => setShowAdminLogin(true)}>Admin</button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-left">
          {/* Quote Section */}
          <div className="hero-quote">
            <blockquote>
              "Bringing authentic flavors and exceptional service to every celebration"
            </blockquote>
            <cite>- Our Culinary Team</cite>
          </div>
          
          <div className="order-box">
            <h3>Order Now</h3>
            <div className="order-tabs">
              <button
                className={orderType === "individual" ? "active" : ""}
                onClick={() => setOrderType("individual")}
              >
                Individual
              </button>
              <button
                className={orderType === "bulk" ? "active" : ""}
                onClick={() => setOrderType("bulk")}
              >
                Bulk Order
              </button>
            </div>
            {orderType === "bulk" && (
              <input
                type="number"
                placeholder="Number of guests"
                value={bulkGuestCount}
                onChange={(e) => setBulkGuestCount(parseInt(e.target.value) || 50)}
                min="10"
                max="1000"
              />
            )}
            <button
              className="view-menu-btn"
              onClick={() => {
                if (orderType === "individual") {
                  setShowMenuPage(true);
                } else {
                  setShowBulkMenu(true);
                }
              }}
            >
              {orderType === "individual" ? "View Menu" : "Start Bulk Order"}
            </button>
          </div>
        </div>

        <div className="hero-right">
          <img src="/images/chef.png" alt="Chef preparing delicious food" />
        </div>
      </section>

      {/* Events Section */}
      <section className="section">
        <h2>Perfect for Any Event</h2>
        <div className="event-grid">
          <div className="event-card" onClick={() => handleEventClick("Weddings")}>
            <div className="event-img">
              <img src="/images/wedding.jpeg" alt="Weddings" />
            </div>
            <h4>Weddings</h4>
            <p>Click to order catering</p>
          </div>
          <div className="event-card" onClick={() => handleEventClick("Corporate Events")}>
            <div className="event-img">
              <img src="/images/corporate.jpg" alt="Corporate Events" />
            </div>
            <h4>Corporate Events</h4>
            <p>Click to order catering</p>
          </div>
          <div className="event-card" onClick={() => handleEventClick("Birthdays")}>
            <div className="event-img">
              <img src="/images/birthday.jpg" alt="Birthdays" />
            </div>
            <h4>Birthdays</h4>
            <p>Click to order catering</p>
          </div>
          <div className="event-card" onClick={() => handleEventClick("Family Gatherings")}>
            <div className="event-img">
              <img src="/images/family.jpeg" alt="Family Gatherings" />
            </div>
            <h4>Family Gatherings</h4>
            <p>Click to order catering</p>
          </div>
        </div>
      </section>

      {/* Specialities Section */}
      <section className="section">
        <h2>Our Specialities</h2>
        <div className="special-grid">
          <div className="special-card">
            <div className="special-img">
              <img src="/images/biriyani.png" alt="Biryani" />
            </div>
            <span>Aromatic Biryani</span>
          </div>
          <div className="special-card">
            <div className="special-img">
              <img src="/images/panner_butter_masala.png" alt="Curries" />
            </div>
            <span>Rich Curries</span>
          </div>
          <div className="special-card">
            <div className="special-img">
              <img src="/images/gulab-jamun.jpg" alt="Desserts" />
            </div>
            <span>Sweet Delights</span>
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="section">
        <h2>Why Choose Us</h2>
        <div className="why-grid">
          <div>
            <h4>Fresh Ingredients</h4>
            <p>We use only the freshest, locally sourced ingredients to ensure the best quality and taste.</p>
          </div>
          <div>
            <h4>Experienced Chefs</h4>
            <p>Our team of experienced chefs brings years of expertise in vegetarian cuisine.</p>
          </div>
          <div>
            <h4>Reliable Service</h4>
            <p>Punctual delivery and excellent service for all your catering needs.</p>
          </div>
        </div>
      </section>

      {/* Reviews Section */}
      <section className="section">
        <h2>What Our Customers Say</h2>
        <div className="review-grid">
          <div>
            <p>"Amazing food and excellent service! Our wedding was perfect thanks to Hotel Shanmuga Bhavaan."</p>
            <strong>- Priya Sharma</strong>
          </div>
          <div>
            <p>"The biryani was absolutely delicious. Will definitely order again for our next event."</p>
            <strong>- Rajesh Kumar</strong>
          </div>
          <div>
            <p>"Professional staff and timely delivery. Highly recommended for any occasion."</p>
            <strong>- Meera Patel</strong>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div>
          <h3>Hotel Shanmuga Bhavaan</h3>
          <p>Delicious vegetarian catering for all occasions</p>
        </div>
        <div>
          <h3>Quick Links</h3>
          <button className="footer-link" onClick={() => setShowMenuPage(true)}>Menu</button>
          <button className="footer-link" onClick={() => setOrderType("bulk")}>Bulk Orders</button>
          <button className="footer-link" onClick={() => setShowAdminLogin(true)}>Admin</button>
        </div>
        <div>
          <h3>Contact Us</h3>
          <p>Phone: 79044 79451</p>
          <p>Email: shanmugapriyaraja31@gmail.com</p>
          <a href="https://maps.app.goo.gl/eE5Gekcffy1RPsZr8" target="_blank" rel="noopener noreferrer" className="location-link">📍 View Location</a>
          <div className="location-icons">
            <span className="location-icon">🗺️</span>
            <span className="location-icon">🧭</span>
            <span className="location-icon">📌</span>
          </div>
        </div>
      </footer>

      {/* Bulk Order Modal */}
      <BulkOrderModal
        isOpen={showBulkOrderModal}
        onClose={handleBulkOrderModalClose}
        onSubmit={handleBulkOrderSubmit}
        eventType={selectedEventType}
      />
    </div>
  );
};

export default App;
