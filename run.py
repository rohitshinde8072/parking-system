import sys
import os
import uvicorn

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath("."))
    print("=" * 65)
    print("  CampusPark AI - Smart Parking Management System")
    port = int(os.getenv("PORT", 8000))
    print(f"  Listening on http://localhost:{port} and 0.0.0.0:{port}")
    print(f"  Swagger API Docs: http://localhost:{port}/docs")
    print("=" * 65)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
