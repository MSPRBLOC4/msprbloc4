# main.py
import uvicorn
from controllers.app import app

if __name__ == "__main__":
    uvicorn.run(
        "controllers.app:app",  # chemin du module et nom de l'instance
        host="0.0.0.0",
        port=8000,
        reload=True            # auto-reload en dev
    )
