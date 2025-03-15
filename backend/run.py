import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload for development
        reload_dirs=["backend"],  # Watch the backend directory for changes
        log_level="info"
    ) 