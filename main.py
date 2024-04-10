import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(
        "labelizer.core.api.fast_api_app:app", port=42042
    )
    server = uvicorn.Server(config)
    server.run()
