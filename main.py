import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(
        "backend.core.api.fast_api_app:app",
        port=42042,
        workers=5,
    )
    server = uvicorn.Server(config)
    server.run()
