from threading import Thread
import time
from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Basic Prometheus metrics
requests_counter = Counter('facebook_plus_requests_total', 'Total HTTP requests')
run_counter = Counter('facebook_plus_runs_total', 'Number of times demo run started')

@app.route('/')
def index():
    requests_counter.inc()
    return "Facebook-Plus: simulation service is up\n"

@app.route('/run')
def run_demo():
    """Trigger the main demo in a background thread; returns immediately."""
    requests_counter.inc()
    run_counter.inc()
    def worker():
        # Import and run the existing main.py logic if available
        try:
            import main
            # If main.py guards with if __name__ == '__main__', call a function instead
            # Fallback: execute main as a script
            # To avoid blocking, run in a separate process if necessary
            try:
                main.__name__ = '__main__'
                # Re-run main logic by calling load if exposed; otherwise execute the file
            except Exception:
                pass
        except Exception as e:
            print('Error running demo:', e)
    Thread(target=worker, daemon=True).start()
    return jsonify({"status": "started"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
