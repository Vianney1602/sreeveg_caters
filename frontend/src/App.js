import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import authService from "./services/authService";
import socketService from "./services/socketService";
import { disableConsoleInProduction } from "./utils/security";
import LoadingAnimation from "./components/LoadingAnimation";
import MenuPage from "./MenuPage";
import CartPage from "./CartPage";
import BulkMenuPage from "./BulkMenuPage";
import BulkCartPage from "./BulkCartPage";
import AdminLogin from "./AdminLogin";
import AdminDashboard from "./AdminDashboard";
import WelcomePage from "./WelcomePage";
import BulkOrderModal from "./BulkOrderModal";
import UserSignUp from "./UserSignUp";
import UserSignIn from "./UserSignIn";
import OrderHistory from "./OrderHistory";
import UserAccount from "./UserAccount";
import "./home.css";

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Security: Disable console in production to prevent data leaks
  useEffect(() => {
    disableConsoleInProduction();
  }, []);
  
  // Check for existing session on mount
  const [initializing, setInitializing] = useState(true);
  const [isPageTransitioning, setIsPageTransitioning] = useState(false);
  const [orderCompleted, setOrderCompleted] = useState(() => {
    // Restore order completion status from sessionStorage
    const saved = sessionStorage.getItem('_orderCompleted');
    return saved === 'true' ? true : false;
  });
  const [orderedItems, setOrderedItems] = useState(() => {
    // Restore ordered items from sessionStorage
    try {
      const saved = sessionStorage.getItem('_orderedItems');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [bulkOrderCompleted, setBulkOrderCompleted] = useState(false);
  const [bulkOrderedItems, setBulkOrderedItems] = useState(() => {
    // Restore bulk ordered items from sessionStorage
    try {
      const saved = sessionStorage.getItem('_bulkOrderedItems');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  
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
  const [showWelcome, setShowWelcome] = useState(false); // Will be set by URL sync or initialization
  const [showUserSignUp, setShowUserSignUp] = useState(false);
  const [showUserSignIn, setShowUserSignIn] = useState(false);
  const [showOrderHistory, setShowOrderHistory] = useState(false);
  const [showUserAccount, setShowUserAccount] = useState(false);
  const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
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

  // Navigation helper functions with loading animation
  const navigateToCart = () => {
    setIsPageTransitioning(true);
    // Reset order state for new order
    setOrderCompleted(false);
    setOrderedItems([]);
    setTimeout(() => {
      navigate('/cart');
      setIsPageTransitioning(false);
    }, 3500);
  };

  const navigateToBulkCart = () => {
    setIsPageTransitioning(true);
    setTimeout(() => {
      navigate('/bulk-cart');
      setIsPageTransitioning(false)
    }, 3500);
  };

  const navigateToBulkMenu = () => {
    setIsPageTransitioning(true);
    setTimeout(() => {
      navigate('/bulk-menu');
      setIsPageTransitioning(false);
    }, 3500);
  };

  // Initialize WebSocket connection on app mount
  useEffect(() => {
    // Set minimum display time for loading animation (6 seconds)
    const minLoadingTime = 6000;
    const startTime = Date.now();

    // Check for existing admin session
    const adminToken = sessionStorage.getItem('_st');
    if (adminToken) {
      // Verify token is still valid
      axios.get('/api/admin/verify', {
        headers: { Authorization: `Bearer ${adminToken}` }
      })
      .then(() => {
        setIsAdminLoggedIn(true);
        // Don't manually set page states - let URL sync handle it
      })
      .catch(() => {
        // Token invalid, clear it
        sessionStorage.removeItem('_st');
        sessionStorage.removeItem('_au');
      })
      .finally(() => {
        // Ensure minimum loading time is met
        const elapsedTime = Date.now() - startTime;
        const remainingTime = Math.max(0, minLoadingTime - elapsedTime);
        setTimeout(() => {
          setInitializing(false);
        }, remainingTime);
      });
    } else {
      // Check for existing user session
      const userToken = sessionStorage.getItem('_userToken');
      const savedUser = sessionStorage.getItem('_user');
      if (userToken && savedUser) {
        try {
          const user = JSON.parse(savedUser);
          // Security: Validate user object has required properties
          if (user && user.id && user.email) {
            setCurrentUser(user);
            setIsUserLoggedIn(true);
          } else {
            // Invalid user data, clear it
            sessionStorage.removeItem('_userToken');
            sessionStorage.removeItem('_user');
          }
        } catch (e) {
          // Invalid user data, clear it
          sessionStorage.removeItem('_userToken');
          sessionStorage.removeItem('_user');
        }
      }
      
      // Restore bulk guest count if exists
      const savedGuestCount = sessionStorage.getItem('_bulkGuestCount');
      if (savedGuestCount) {
        setBulkGuestCount(parseInt(savedGuestCount));
      }

      // Don't set showWelcome here - let the URL sync effect handle it
      // This prevents conflicts with browser navigation

      // Ensure minimum loading time is met
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, minLoadingTime - elapsedTime);
      setTimeout(() => {
        setInitializing(false);
      }, remainingTime);
    }
    
    const token = sessionStorage.getItem('_userToken'); // User token in sessionStorage
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
  
  // Security: Detect and prevent history manipulation attacks
  useEffect(() => {
    const handlePopState = (event) => {
      // Security: Clear sensitive data from history state
      if (event.state && typeof event.state === 'object') {
        // Sanitize any sensitive data that might be in history state
        const sanitizedState = {};
        window.history.replaceState(sanitizedState, '', window.location.pathname);
      }
    };
    
    window.addEventListener('popstate', handlePopState);
    
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);
  
  // Security: Prevent data leaks through page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is hidden - could implement auto-lock or data clearing
        // Currently monitoring only - add logic if needed
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);
  
  // Persist order completion status
  useEffect(() => {
    sessionStorage.setItem('_orderCompleted', orderCompleted ? 'true' : 'false');
  }, [orderCompleted]);
  
  // Persist ordered items
  useEffect(() => {
    sessionStorage.setItem('_orderedItems', JSON.stringify(orderedItems));
  }, [orderedItems]);
  
  // Persist bulk ordered items
  useEffect(() => {
    sessionStorage.setItem('_bulkOrderedItems', JSON.stringify(bulkOrderedItems));
  }, [bulkOrderedItems]);
  
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
  
  // Synchronize page state with URL for browser back/forward button support
  useEffect(() => {
    if (initializing) return; // Don't sync during initialization
    
    const path = location.pathname;
    
    // Security: Validate URL to prevent injection attacks
    const validPaths = ['/', '/menu', '/cart', '/bulk-menu', '/bulk-cart', '/admin-login', 
                        '/admin', '/signup', '/signin', '/order-history', '/account'];
    if (!validPaths.includes(path)) {
      // Invalid path detected - redirect to home
      navigate('/', { replace: true });
      return;
    }
    
    // Determine which page should be shown based on URL
    // This prevents multiple state updates and re-renders
    let pageState = {
      menu: false,
      cart: false,
      bulkMenu: false,
      bulkCart: false,
      adminLogin: false,
      signup: false,
      signin: false,
      orderHistory: false,
      account: false,
      welcome: false
    };
    
    if (path === '/menu') {
      pageState.menu = true;
    } else if (path === '/cart') {
      pageState.cart = true;
    } else if (path === '/bulk-menu') {
      pageState.bulkMenu = true;
    } else if (path === '/bulk-cart') {
      pageState.bulkCart = true;
    } else if (path === '/admin-login') {
      pageState.adminLogin = true;
    } else if (path === '/admin') {
      // Admin dashboard - verify admin is logged in or has valid token
      const adminToken = sessionStorage.getItem('_st');
      if (!isAdminLoggedIn && !adminToken) {
        // Not admin, redirect to signin
        navigate('/signin', { replace: true });
        return;
      }
      // Admin is logged in or has token - all pageState flags stay false so admin dashboard renders
    } else if (path === '/signup') {
      pageState.signup = true;
    } else if (path === '/signin') {
      // If already admin, redirect to admin dashboard
      if (isAdminLoggedIn) {
        navigate('/admin', { replace: true });
        return;
      }
      pageState.signin = true;
    } else if (path === '/order-history') {
      // Security: Only allow if user is logged in
      pageState.orderHistory = isUserLoggedIn;
      if (!isUserLoggedIn) {
        navigate('/signin', { replace: true });
        return;
      }
    } else if (path === '/account') {
      // Allow if user is logged in or currentUser exists
      pageState.account = isUserLoggedIn || !!currentUser;
      if (!isUserLoggedIn && !currentUser) {
        navigate('/signin', { replace: true });
        return;
      }
    } else if (path === '/' || path === '') {
      // If admin is logged in, redirect to admin dashboard
      if (isAdminLoggedIn) {
        navigate('/admin', { replace: true });
        return;
      }
      // Show welcome page only if neither admin nor user is logged in
      pageState.welcome = !isAdminLoggedIn && !isUserLoggedIn;
    }
    
    // Update all states in one batch to prevent glitching
    setShowMenuPage(pageState.menu);
    setShowCart(pageState.cart);
    setShowBulkMenu(pageState.bulkMenu);
    setShowBulkCart(pageState.bulkCart);
    setShowAdminLogin(pageState.adminLogin);
    setShowUserSignUp(pageState.signup);
    setShowUserSignIn(pageState.signin);
    setShowOrderHistory(pageState.orderHistory);
    setShowUserAccount(pageState.account);
    setShowWelcome(pageState.welcome);
  }, [location.pathname, isAdminLoggedIn, isUserLoggedIn, initializing]);
  
  // Require authentication - redirect to welcome if not logged in and not on auth pages
  useEffect(() => {
    if (initializing) return; // Don't redirect during initialization
    
    const path = location.pathname;
    const isOnAuthPage = path === '/' || path === '/signup' || path === '/signin' || 
                         path === '/admin-login' || path === '/admin';
    
    if (!isUserLoggedIn && !isAdminLoggedIn && !isOnAuthPage) {
      navigate('/');
    }
  }, [isUserLoggedIn, isAdminLoggedIn, location.pathname, initializing, navigate]);
  
  const [paymentStatus, setPaymentStatus] = useState(null); // For payment feedback
  // Dashboard Stats (if needed)
  const [dashboardStats, setDashboardStats] = useState({});

  // Configure axios once on mount
  useEffect(() => {
    const API_BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";
    axios.defaults.baseURL = API_BASE_URL;
    axios.defaults.headers.post["Content-Type"] = "application/json";
    axios.defaults.timeout = 60000; // 60 second timeout for all requests
    
    // Security: Add request interceptor to include auth tokens
    const requestInterceptor = axios.interceptors.request.use(
      config => {
        // Add user token if available
        const userToken = sessionStorage.getItem('_userToken');
        if (userToken && !config.headers.Authorization) {
          config.headers.Authorization = `Bearer ${userToken}`;
        }
        return config;
      },
      error => Promise.reject(error)
    );
    
    // Add response interceptor for error handling and security
    const responseInterceptor = axios.interceptors.response.use(
      response => response,
      error => {
        // Security: Handle unauthorized access (401)
        if (error.response && error.response.status === 401) {
          // Token expired or invalid - clear auth data
          const adminToken = sessionStorage.getItem('_st');
          if (adminToken) {
            sessionStorage.removeItem('_st');
            sessionStorage.removeItem('_au');
            setIsAdminLoggedIn(false);
            navigate('/admin-login');
          } else {
            sessionStorage.removeItem('_userToken');
            sessionStorage.removeItem('_user');
            setIsUserLoggedIn(false);
            setCurrentUser(null);
            navigate('/');
          }
        }
        
        // Security: Handle forbidden access (403)
        if (error.response && error.response.status === 403) {
          console.error('Access forbidden');
          navigate('/');
        }
        
        return Promise.reject(error);
      }
    );
    
    return () => {
      // Cleanup interceptors on unmount
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [navigate, setIsAdminLoggedIn, setIsUserLoggedIn, setCurrentUser]);

  // Payment function using Razorpay (LIVE MODE)
  const initiatePayment = (orderId, amount, customerDetails, onSuccess, onError) => {
    const razorpayKey = process.env.REACT_APP_RAZORPAY_KEY;
    if (!razorpayKey) {
      console.error('Razorpay key not configured');
      if (onError) onError(new Error('Payment configuration error'));
      return;
    }
    const options = {
      key: razorpayKey,
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

  const updateBulkQty = (id, qty) => {
    setBulkCart((prev) => {
      if (!prev[id]) return prev;
      const numericQty = parseInt(qty, 10);
      const safeQty = Number.isFinite(numericQty) && numericQty > 0 ? numericQty : 1;
      return { ...prev, [id]: { ...prev[id], qty: safeQty } };
    });
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
    navigate('/bulk-menu');
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
  //       alert('Error submitting booking.');
  //     });
  // };

  // Admin login (legacy - not currently used)
  // eslint-disable-next-line no-unused-vars
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

  // --- Conditional renders ---
  if (initializing) return <LoadingAnimation />;
  if (isPageTransitioning) return <LoadingAnimation />;
  
  // Admin dashboard: check if admin is logged in OR if admin token exists (for immediate navigation after login)
  const adminToken = sessionStorage.getItem('_st');
  if (isAdminLoggedIn || (adminToken && location.pathname === '/admin')) {
    // Security: Verify admin token still exists
    if (!adminToken) {
      setIsAdminLoggedIn(false);
      navigate('/signin', { replace: true });
      return null;
    }
    // Ensure isAdminLoggedIn state is synced
    if (!isAdminLoggedIn) {
      setIsAdminLoggedIn(true);
    }
    return (
      <AdminDashboard
        onLogout={() => {
          authService.logout();
          setIsAdminLoggedIn(false);
          sessionStorage.removeItem('_currentPage');
          sessionStorage.removeItem('_st');
          sessionStorage.removeItem('_au');
          window.history.replaceState(null, '', '/');
          navigate('/', { replace: true });
        }}
        stats={dashboardStats}
      />
    );
  }
  if (showAdminLogin) {
    return (
      <AdminLogin
        goBack={() => navigate(-1)}
        onLoginSuccess={() => {
          setIsAdminLoggedIn(true);
          navigate('/admin');
        }}
      />
    );
  }
  if (showWelcome) return <WelcomePage onGetStarted={() => navigate('/signin')} />;
  if (showUserSignUp) return <UserSignUp goToSignIn={() => navigate('/signin')} goBack={() => navigate(-1)} onSignUpSuccess={(user) => {
    const adminEmails = ['admin@shanmugabhavaan.com'];
    if (adminEmails.includes(user.email)) {
      // Admin signup: set admin session properly
      const userToken = sessionStorage.getItem('_userToken');
      if (userToken) {
        sessionStorage.setItem('_st', userToken); // Set admin token
      }
      sessionStorage.removeItem('_userToken');
      sessionStorage.removeItem('_user');
      sessionStorage.setItem('_showWelcome', 'false');
      setIsUserLoggedIn(false);
      setCurrentUser(null);
      setIsAdminLoggedIn(true);
      // Use replace to prevent back button returning to signup
      navigate('/admin', { replace: true });
    } else {
      setCurrentUser(user);
      setIsUserLoggedIn(true);
      setShowUserAccount(true);
      sessionStorage.setItem('_showWelcome', 'false');
      navigate('/account');
    }
  }} goToHome={() => navigate('/')} />;
  if (showUserSignIn) return <UserSignIn goToSignUp={() => navigate('/signup')} goBack={() => navigate(-1)} onSignInSuccess={(user) => {
    const adminEmails = ['admin@shanmugabhavaan.com'];
    if (adminEmails.includes(user.email)) {
      // Admin login: set admin session properly
      const userToken = sessionStorage.getItem('_userToken');
      if (userToken) {
        sessionStorage.setItem('_st', userToken); // Set admin token
      }
      sessionStorage.removeItem('_userToken');
      sessionStorage.removeItem('_user');
      sessionStorage.setItem('_showWelcome', 'false');
      setIsUserLoggedIn(false);
      setCurrentUser(null);
      setIsAdminLoggedIn(true);
      // Use replace to prevent back button returning to signin
      navigate('/admin', { replace: true });
    } else {
      setCurrentUser(user);
      setIsUserLoggedIn(true);
      setShowUserAccount(true);
      sessionStorage.setItem('_showWelcome', 'false');
      navigate('/account');
    }
  }} goToHome={() => navigate('/')} />;
  if (showOrderHistory) {
    if (!isUserLoggedIn || !currentUser) {
      navigate('/signin');
      return null;
    }
    return <OrderHistory user={currentUser} goBack={() => navigate(-1)} />;
  }
  if (showUserAccount) {
    if (!isUserLoggedIn || !currentUser) {
      navigate('/signin');
      return null;
    }
    return <UserAccount user={currentUser} onLogout={() => {
      setIsUserLoggedIn(false);
      setCurrentUser(null);
      sessionStorage.removeItem('_userToken');
      sessionStorage.removeItem('_user');
      navigate('/signin');
    }} goToOrderHistory={() => navigate('/order-history')} goToMenu={() => navigate('/menu')} goToHome={() => navigate('/')} />;
  }
  if (showCart)
    return (
      <CartPage
        goBack={() => {
          navigate(-1);
        }}
        cart={cart}
        updateQty={updateQty}
        clearCart={() => setCart({})}
        initiatePayment={initiatePayment}
        paymentStatus={paymentStatus}
        clearPaymentStatus={() => setPaymentStatus(null)}
        orderCompleted={orderCompleted}
        setOrderCompleted={setOrderCompleted}
        orderedItems={orderedItems}
        setOrderedItems={setOrderedItems}
      />
    );
  if (showMenuPage)
    return (
      <MenuPage
        goBack={() => {
          navigate(-1);
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
          navigate(-1);
        }}
      />
    );
  if (showBulkCart)
    return (
      <BulkCartPage
        guestCount={bulkGuestCount}
        bulkCart={bulkCart}
        updateBulkQty={updateBulkQty}
        goBack={navigateToBulkMenu}
        clearCart={() => setBulkCart({})}
        initiatePayment={initiatePayment}
        defaultPaymentMethod="online"
        paymentStatus={paymentStatus}
        clearPaymentStatus={() => setPaymentStatus(null)}
        bulkOrderCompleted={bulkOrderCompleted}
        setBulkOrderCompleted={setBulkOrderCompleted}
        bulkOrderedItems={bulkOrderedItems}
        setBulkOrderedItems={setBulkOrderedItems}
      />
    );

  // Packages hardcoded (can also fetch from backend if needed - legacy)
  // eslint-disable-next-line no-unused-vars
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
        <div className="header-brand">
          <h2 className="header-title">Hotel Shanmuga Bhavaan</h2>
        </div>
        <nav className="header-nav" aria-label="Primary">
          <button onClick={() => navigate('/menu')}>View Menu</button>
          <span className="nav-separator" aria-hidden="true">|</span>
          <button onClick={() => navigate('/cart')}>
            Cart
          </button>
          <span className="nav-separator" aria-hidden="true">|</span>
          <button onClick={() => {
            if (isAdminLoggedIn) {
              navigate('/admin');
            } else if (currentUser) {
              setShowUserAccount(true);
              navigate('/account');
            } else {
              navigate('/signin');
            }
          }}>
            My Account
          </button>
        </nav>
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
                  navigate('/menu');
                } else {
                  navigate('/bulk-menu');
                }
              }}
            >
              {orderType === "individual" ? "View Menu" : "Start Bulk Order"}
            </button>
          </div>
        </div>

        <div className="hero-right">
          <img src="/images/chefs.png" alt="Chef preparing delicious food" />
        </div>
      </section>

      {/* Events Section */}
      <section className="section">
        <h2>Perfect for Any Event</h2>
        <div className="event-grid">
          <div className="event-card" onClick={() => handleEventClick("Weddings")}>
            <div className="event-img">
              <img src="/images/wedding.webp" alt="Weddings" />
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
              <img src="/images/birthday.png" alt="Birthdays" />
            </div>
            <h4>Birthdays</h4>
            <p>Click to order catering</p>
          </div>
          <div className="event-card" onClick={() => handleEventClick("Family Gatherings")}>
            <div className="event-img">
              <img src="/images/family.png" alt="Family Gatherings" />
            </div>
            <h4>Family Gatherings</h4>
            <p>Click to order catering</p>
          </div>
        </div>
      </section>

      {/* Specialities Section */}
      <section className="section">
        <h2 className="section-title">Our Specialities</h2>
        <div className="special-grid">
          <div className="special-card">
            <div className="special-img">
              <img src="/images/tiffin-items.png" alt="Tiffin Speciality"/>
            </div>
            <span style={{ fontFamily: 'cursive', fontWeight: 'bold', fontSize: '1.2em' }}>Tiffin</span>
          </div>
          <div className="special-card">
            <div className="special-img">
              <img src="/images/Lunch-items.png" alt="Lunch Speciality"/>
            </div>
            <span style={{ fontFamily: 'cursive', fontWeight: 'bold', fontSize: '1.2em' }}>Lunch</span>
          </div>
          <div className="special-card">
            <div className="special-img">
              <img src="/images/dinner-items.png" alt="Dinner Speciality"/>
            </div>
            <span style={{ fontFamily: 'cursive', fontWeight: 'bold', fontSize: '1.2em' }}>Dinner</span>
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
            <p>Our team of experienced chefs brings years of expertise in vegetarian cuiHey isine.</p>
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
          <button className="footer-link" onClick={() => navigate('/menu')}>Menu</button>
          <button className="footer-link" onClick={() => navigate('/cart')}>Cart</button>
          <button className="footer-link" onClick={() => navigate('/account')}>My Account</button>
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
