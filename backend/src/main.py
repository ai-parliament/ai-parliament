import os
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import create_app

# Load environment variables
load_dotenv()

# Create the FastAPI application
app = create_app()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Start the server
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )