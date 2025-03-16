import time

def add_timestamp(request):
    """Add current timestamp to context for cache-busting."""
    return {'CURRENT_TIMESTAMP': int(time.time())} 