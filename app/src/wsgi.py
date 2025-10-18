"""
WSGI/Gunicorn wrapper for chicken coop application.

This module provides a gunicorn-compatible entry point that runs the
asyncio-based chicken coop application in a background thread.
"""

import threading
from door2 import main

# Global flag to track if the application is running
_running = False
_thread = None


def application(environ, start_response):
    """
    Dummy WSGI application for gunicorn compatibility.

    The actual chicken coop application runs in a background thread.
    This WSGI app just keeps gunicorn alive and responds to health checks.
    """
    global _running, _thread

    # Start the application in a background thread if not already running
    if not _running:
        _running = True
        _thread = threading.Thread(target=main, daemon=True)
        _thread.start()

    # Simple health check response
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)

    return [b'Chicken Coop Application Running\n']


# For gunicorn with the call syntax: 'wsgi:application'
__all__ = ['application']
