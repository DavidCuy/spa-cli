from fastapi import FastAPI, Request
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os
import json

load_dotenv()

env = os.getenv('ENVIRONMENT', 'dev')
SCHEMA_PATH = Path(__file__).parent / "openapi.json"

app = FastAPI(
    title='Test API',
    description='API ',
    openapi_url="/openapi.json"
)
app.openapi_schema = json.loads(SCHEMA_PATH.read_text())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api_local.router import router
app.include_router(router, prefix=f"/{env.lower() or 'v1'}")


@app.get("/")
def read_root(request: Request):
    return {
        "Message": "Api deployed",
        "Configuration": {
            "environment": env,
            "server": {
                "host": os.getenv('SERVER_HOST', '127.0.0.1'),
                "port": os.getenv('SERVER_PORT', '8000'),
                "reload": os.getenv('SERVER_RELOAD', 'true') == 'true',
                "log_level": os.getenv('SERVER_LOG_LEVEL', 'info'),
                "root_path": os.getenv('SERVER_ROOT_PATH', ''),
                "proxy_headers": os.getenv('SERVER_PROXY_HEADERS', 'false') == 'true'
            },
            "request": {
                "client_host": request.client.host if request.client else "unknown",
                "base_url": str(request.base_url),
                "url": str(request.url)
            },
            "api": {
                "prefix": f"/{env.lower() or 'v1'}",
                "openapi_url": "/openapi.json",
                "docs_url": "/docs",
                "redoc_url": "/redoc"
            }
        }
    }


# to make it work with Amazon Lambda, we create a handler object
handler = Mangum(app=app)

