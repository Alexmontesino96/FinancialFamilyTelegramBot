"""
Health Check Module

This module provides a simple HTTP server for health checks.
It is used by Render to verify that the application is running correctly.
"""

import http.server
import socketserver
import threading
from config import logger

# Define the port to listen on
PORT = 10000

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for health check requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            # Return 200 OK for health checks
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            # Return 404 for other paths
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Override to use our logger instead of printing to stderr."""
        logger.info("%s - - [%s] %s" %
                    (self.address_string(),
                     self.log_date_time_string(),
                     format % args))

def start_health_check_server():
    """Start the health check server in a separate thread."""
    try:
        handler = HealthCheckHandler
        httpd = socketserver.TCPServer(("", PORT), handler)
        logger.info(f"Starting health check server on port {PORT}")
        
        # Start the server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True  # So the thread will exit when the main thread exits
        server_thread.start()
        
        return httpd
    except Exception as e:
        logger.error(f"Failed to start health check server: {e}")
        return None 