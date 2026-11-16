import sys
import time
import threading
import webbrowser

# Ensure Starlette 1.0+ compatibility with FastAPI 0.110
import starlette.routing
_orig_router_init = starlette.routing.Router.__init__
def _patched_router_init(self, *args, **kwargs):
    kwargs.pop('on_startup', None)
    kwargs.pop('on_shutdown', None)
    return _orig_router_init(self, *args, **kwargs)
starlette.routing.Router.__init__ = _patched_router_init

from fastapi import FastAPI
FastAPI.max_body_size = None

import uvicorn

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("\n" + "=" * 76)
    print("  🚀  StartupLens AI — Indian Startup Valuation & Investor Intelligence")
    print("  👨‍💻  Author: Dhruval | AIML Project Suite")
    print("=" * 76)
    print("  🌐  Interactive Web Dashboard:   http://127.0.0.1:8000")
    print("  📚  Swagger REST API Docs:       http://127.0.0.1:8000/docs")
    print("  📊  ReDoc Schema Explorer:       http://127.0.0.1:8000/redoc")
    print("  🎯  Streamlit Alternate App:     streamlit run streamlit_app.py")
    print("=" * 76 + "\n")

    # Automatically launch browser if --no-browser flag is not present
    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
