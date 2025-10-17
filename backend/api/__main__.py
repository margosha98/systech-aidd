"""Entry point для запуска API сервера."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
