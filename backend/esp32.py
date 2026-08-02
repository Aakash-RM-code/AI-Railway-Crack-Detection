"""
ESP32 Controller for Railway Rover
Production-quality HTTP client with retry logic, caching, and thread-safety
"""
import json
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from queue import Queue, Empty

from config import (
    ESP32_BASE_URL, ESP32_TIMEOUT, ESP32_RETRIES, 
    ESP32_RETRY_DELAY, DEFAULT_SPEED, MIN_SPEED, MAX_SPEED
)

logger = logging.getLogger(__name__)


class ESP32Controller:
    """
    Thread-safe controller for ESP32 railway rover.
    Handles all HTTP communication with retry logic and caching.
    """
    
    def __init__(self, base_url: str = ESP32_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.timeout = ESP32_TIMEOUT
        self.retries = ESP32_RETRIES
        self.retry_delay = ESP32_RETRY_DELAY
        
        # Thread safety
        self._lock = threading.RLock()
        self._polling_thread = None
        self._polling_active = False

        # Command queue: commands are enqueued from any thread and executed
        # only on the single background polling thread (never on the UI thread).
        self._command_queue: "Queue" = Queue()
        self._coalesced: Dict[str, Any] = {}
        self._command_debounce: Dict[str, float] = {}
        self._last_send_time: Dict[str, float] = {}

        # Cache
        self._last_status: Optional[Dict[str, Any]] = None
        self._last_gps: Optional[str] = None
        self._last_gps_data: Optional[Tuple[float, float]] = None
        self._online: bool = False
        self._last_communication: Optional[datetime] = None
        self._last_error: Optional[str] = None
        
        # Session with retry strategy
        self._session = self._create_session()
        
        logger.info(f"ESP32Controller initialized with base URL: {base_url}")
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers
        session.headers.update({
            'User-Agent': 'ESP32-Rover-Control/1.0',
            'Accept': '*/*'
        })
        
        return session
    
    def _make_request(self, endpoint: str, parse_json: bool = False) -> Optional[Any]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            endpoint: API endpoint (e.g., '/status')
            parse_json: Whether to parse response as JSON
            
        Returns:
            Parsed response or None on failure
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            with self._lock:
                response = self._session.get(
                    url, 
                    timeout=self.timeout
                )
                
                # Update online status
                self._online = True
                self._last_communication = datetime.now()
                
                # Check response
                response.raise_for_status()
                
                # Parse response
                if parse_json:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON response from {endpoint}: {response.text[:100]}")
                        return None
                else:
                    return response.text
                    
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            with self._lock:
                self._online = False
                self._last_error = error_msg
            logger.warning(f"Request failed for {endpoint}: {error_msg}")
            return None
    
    def submit(self, command, *args, key=None, debounce=0.0):
        """
        Enqueue a command to run on the background polling thread.
        Never blocks; safe to call from the UI thread.
        
        Args:
            command: callable to execute (e.g. self.forward)
            *args: arguments passed to the callable
            key: optional coalescing key. If a command with the same key is
                 already queued, it is replaced by this one (latest wins),
                 which debounces bursts such as slider drags.
            debounce: minimum seconds between two executions of the same key
        """
        def _run():
            return command(*args)

        if key is not None:
            with self._lock:
                self._coalesced[key] = _run
                self._command_debounce[key] = debounce
        else:
            self._command_queue.put(_run)
    
    # ==================== Public API Methods ====================
    
    def connect(self) -> bool:
        """
        Test connection to ESP32.
        
        Returns:
            bool: True if connected successfully
        """
        result = self._make_request('/status', parse_json=True)
        if result:
            self._last_status = result
            self._online = True
            logger.info("ESP32 connection successful")
            return True
        
        self._online = False
        logger.warning("ESP32 connection failed")
        return False
    
    def forward(self) -> str:
        """Move rover forward"""
        response = self._make_request('/forward')
        return response or "ERROR"
    
    def backward(self) -> str:
        """Move rover backward"""
        response = self._make_request('/backward')
        return response or "ERROR"
    
    def stop(self) -> str:
        """Stop rover"""
        response = self._make_request('/stop')
        return response or "ERROR"
    
    def set_speed(self, speed: int) -> bool:
        """
        Set rover speed.
        
        Args:
            speed: Speed value (0-255)
            
        Returns:
            bool: True if successful
        """
        speed = max(MIN_SPEED, min(MAX_SPEED, speed))
        response = self._make_request(f'/speed?val={speed}')
        
        if response:
            # Update cached status if available
            if self._last_status:
                with self._lock:
                    self._last_status['speed'] = speed
            return True
        
        return False
    
    def get_status(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get rover status.
        
        Args:
            force_refresh: Force HTTP request instead of using cache
            
        Returns:
            Status dict or None on failure
        """
        if not force_refresh and self._last_status:
            return self._last_status.copy()
        
        result = self._make_request('/status', parse_json=True)
        if result:
            with self._lock:
                self._last_status = result
            return result
        
        # Return cached status if available
        return self._last_status.copy() if self._last_status else None
    
    def get_gps(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get GPS location.
        
        Args:
            force_refresh: Force HTTP request instead of using cache
            
        Returns:
            GPS string (e.g., "12.923456,80.123456") or None on failure
        """
        if not force_refresh and self._last_gps:
            return self._last_gps
        
        result = self._make_request('/gps')
        if result:
            with self._lock:
                self._last_gps = result.strip()
                # Parse GPS data if valid
                if result.strip() != "NO_FIX":
                    try:
                        lat, lon = map(float, result.strip().split(','))
                        self._last_gps_data = (lat, lon)
                    except (ValueError, AttributeError):
                        self._last_gps_data = None
                else:
                    self._last_gps_data = None
            return self._last_gps
        
        # Return cached GPS if available
        return self._last_gps
    
    def get_gps_coordinates(self) -> Optional[Tuple[float, float]]:
        """
        Get GPS coordinates as tuple.
        
        Returns:
            Tuple of (latitude, longitude) or None if no fix
        """
        # Ensure GPS is updated
        self.get_gps()
        return self._last_gps_data
    
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Send SMS via ESP32 GSM module.
        
        Args:
            phone: Phone number
            message: SMS message
            
        Returns:
            bool: True if sent successfully
        """
        import urllib.parse
        phone_encoded = urllib.parse.quote(phone)
        message_encoded = urllib.parse.quote(message)
        
        response = self._make_request(f'/sms?phone={phone_encoded}&message={message_encoded}')
        return response == "SMS_SENT" if response else False
    
    def send_test_sms(self) -> bool:
        """Send test SMS using configured phone number"""
        response = self._make_request('/sms_test')
        return response == "SMS_SENT" if response else False
    
    def emergency_stop(self) -> bool:
        """
        Emergency stop - calls /crack_stop endpoint.
        ESP32 firmware handles: stop motors, read GPS, send SMS.
        
        Returns:
            bool: True if successful
        """
        logger.warning("⚠️ EMERGENCY STOP ACTIVATED")
        response = self._make_request('/crack_stop')
        
        if response == "CRACK_STOPPED":
            # Clear cache status
            with self._lock:
                if self._last_status:
                    self._last_status['moving'] = False
                    self._last_status['direction'] = 'STOP'
            return True
        
        return False
    
    # ==================== Status Methods ====================
    
    def is_online(self) -> bool:
        """Check if ESP32 is online"""
        with self._lock:
            return self._online
    
    def get_last_communication(self) -> Optional[datetime]:
        """Get timestamp of last successful communication"""
        with self._lock:
            return self._last_communication
    
    def last_error(self) -> Optional[str]:
        """Get the last error message"""
        with self._lock:
            return self._last_error

    def get_cached_status(self) -> Optional[Dict[str, Any]]:
        """Get cached status without making HTTP request"""
        with self._lock:
            return self._last_status.copy() if self._last_status else None
    
    def get_cached_gps(self) -> Optional[str]:
        """Get cached GPS without making HTTP request"""
        with self._lock:
            return self._last_gps
    
    # ==================== Polling ====================
    
    def start_polling(self, interval: float = 2.0):
        """
        Start background polling thread.
        
        Args:
            interval: Polling interval in seconds
        """
        if self._polling_thread and self._polling_thread.is_alive():
            logger.warning("Polling thread already running")
            return
        
        self._polling_active = True
        self._polling_thread = threading.Thread(
            target=self._polling_loop,
            args=(interval,),
            daemon=True,
            name="ESP32PollingThread"
        )
        self._polling_thread.start()
        logger.info(f"Polling thread started (interval={interval}s)")
    
    def stop_polling(self):
        """Stop background polling thread"""
        self._polling_active = False
        if self._polling_thread:
            self._polling_thread.join(timeout=3.0)
        logger.info("Polling thread stopped")
    
    def _polling_loop(self, interval: float):
        """Single background thread: drains queued commands frequently and
        polls /status + /gps at `interval`. All HTTP runs off the UI thread."""
        next_poll = time.time()
        while self._polling_active:
            try:
                self._drain_commands()
                if time.time() >= next_poll:
                    # Update status
                    self.get_status(force_refresh=True)
                    # Update GPS
                    self.get_gps(force_refresh=True)
                    next_poll = time.time() + interval
            except Exception as e:
                logger.error(f"Polling error: {str(e)}")
            time.sleep(0.1)
    
    def _drain_commands(self):
        """Execute all queued commands (FIFO) then the latest coalesced
        command per key, honoring per-key debounce windows."""
        # Coalesced commands (latest wins per key)
        with self._lock:
            coalesced = dict(self._coalesced)
            debounce_map = dict(self._command_debounce)
            self._coalesced = {}
            self._command_debounce = {}
        now = time.time()
        for key, cmd in coalesced.items():
            last = self._last_send_time.get(key, 0.0)
            if now - last < debounce_map.get(key, 0.0):
                with self._lock:
                    self._coalesced[key] = cmd
                    self._command_debounce[key] = debounce_map[key]
                continue
            self._last_send_time[key] = now
            try:
                cmd()
            except Exception as e:
                logger.error(f"Command failed ({key}): {str(e)}")

        # FIFO commands
        while True:
            try:
                cmd = self._command_queue.get_nowait()
            except Empty:
                break
            try:
                cmd()
            except Exception as e:
                logger.error(f"Command failed: {str(e)}")
    
    # ==================== Cleanup ====================
    
    def close(self):
        """Clean up resources"""
        self.stop_polling()
        if self._session:
            self._session.close()
        logger.info("ESP32Controller closed")