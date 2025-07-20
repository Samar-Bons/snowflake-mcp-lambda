// ABOUTME: Authentication event system for coordinating logout across the app
// ABOUTME: Allows API client to signal AuthProvider when 401 errors occur

type AuthEventType = 'logout';
type AuthEventListener = () => void;

class AuthEventEmitter {
  private listeners: Map<AuthEventType, AuthEventListener[]> = new Map();

  on(event: AuthEventType, listener: AuthEventListener) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }

  off(event: AuthEventType, listener: AuthEventListener) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(listener);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  emit(event: AuthEventType) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(listener => listener());
    }
  }
}

export const authEvents = new AuthEventEmitter();
