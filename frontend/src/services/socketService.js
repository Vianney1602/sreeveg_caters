import { io } from 'socket.io-client';

// Use backend API URL from environment or default to localhost
const SOCKET_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  /**
   * Initialize and connect to the WebSocket server
   * @param {string} token - JWT authentication token
   */
  connect(token = null) {
    if (this.socket && this.isConnected) {
      return;
    }

    const options = {
      // Backend is configured for long-polling only (allow_upgrades=False)
      transports: ['polling'],
      upgrade: false,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      auth: token ? { token } : {}
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
    });

    this.socket.on('disconnect', (reason) => {
      this.isConnected = false;
    });

    this.socket.on('connect_error', (error) => {
      // Silent error handling
    });

    this.socket.on('reconnect', (attemptNumber) => {
      // Silent reconnect
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
    if (this.socket && this.isConnected) {
      this.emit('join', { room });
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
