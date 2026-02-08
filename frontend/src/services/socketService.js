import { io } from 'socket.io-client';

// Use backend API URL from environment
const SOCKET_URL = process.env.REACT_APP_API_BASE_URL;

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.lastToken = null;
  }

  /**
   * Initialize and connect to the WebSocket server
   * @param {string} token - JWT authentication token
   */
  connect(token = null) {
    // If a new token is provided and differs from the last one, reconnect with it
    if (token && token !== this.lastToken) {
      this.disconnect();
      this.lastToken = token;
    } else if (!this.lastToken && token) {
      this.lastToken = token;
    }

    if (this.socket && this.isConnected) {
      return this.socket;
    }

    const options = {
      // Backend is configured for long-polling only (allow_upgrades=False)
      transports: ['polling'],
      upgrade: false,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      auth: this.lastToken ? { token: this.lastToken } : {}
    };

    this.socket = io(SOCKET_URL, options);

    // Global listener for ALL events (must be attached immediately)
    this.socket.onAny((eventName, ...args) => {
      try {
        // Silent - no logging
      } catch (e) {
        // noop
      }
    });

    // Connection event handlers
    this.socket.on('connect', () => {
      this.isConnected = true;
      console.log('Socket.IO connected');
    });

    this.socket.on('disconnect', (reason) => {
      this.isConnected = false;
      console.log('Socket.IO disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.log('Socket.IO connection error:', error.message);
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('Socket.IO reconnected after', attemptNumber, 'attempts');
    });

    this.socket.on('reconnect_attempt', (attemptNumber) => {
      // Silent reconnect attempt
    });

    this.socket.on('reconnect_error', (error) => {
      // Silent error
    });

    this.socket.on('reconnect_failed', () => {
      // Silent failure
    });

    return this.socket;
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  /**
   * Emit an event to the server
   * @param {string} event - Event name
   * @param {*} data - Data to send
   * @param {function} callback - Optional callback function
   */
  emit(event, data, callback) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data, callback);
    }
  }

  /**
   * Listen for events from the server
   * @param {string} event - Event name to listen for
   * @param {function} callback - Callback function to handle the event
   */
  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  /**
   * Remove event listener
   * @param {string} event - Event name
   * @param {function} callback - Optional specific callback to remove
   */
  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  /**
   * Join a specific room for targeted messaging
   * @param {string} room - Room name to join
   */
  joinRoom(room) {
    if (this.socket) {
      // If already connected, join immediately
      if (this.isConnected) {
        this.socket.emit('join', { room });
      } else {
        // If not connected yet, wait for connection then join
        this.socket.once('connect', () => {
          this.socket.emit('join', { room });
        });
      }
    }
  }

  /**
   * Leave a specific room
   * @param {string} room - Room name to leave
   */
  leaveRoom(room) {
    if (this.socket && this.isConnected) {
      this.emit('leave', { room });
    }
  }

  /**
   * Get connection status
   * @returns {boolean} - Whether socket is connected
   */
  getConnectionStatus() {
    return this.isConnected;
  }

  /**
   * Get the socket instance
   * @returns {Socket} - Socket.IO client instance
   */
  getSocket() {
    return this.socket;
  }
}

// Create and export a singleton instance
const socketService = new SocketService();
export default socketService;
