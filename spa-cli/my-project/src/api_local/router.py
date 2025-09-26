from fastapi import APIRouter
from fastapi import Request
from fastapi import Body, Header, Query, Response
from core_http.utils import get_body, get_status_code
import json
import base64
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, List, Any, cast

class MockContext:
    def __init__(self):
        self.function_name = "role_users_report"
        self.memory_limit_in_mb = 50
        self.invoked_function_arn = "arn:aws:lambda:aws-region-1:123456789012:function:role_users_report"
        self.aws_request_id = str(uuid.uuid4())

async def build_event_from_request(request: Request) -> Dict[str, Any]:
    path_parameters = request.path_params
    body_bytes = await request.body()
    try:
        body_str = body_bytes.decode('utf-8') if body_bytes else None
    except UnicodeDecodeError:
        body_str = base64.b64encode(body_bytes).decode('utf-8') if body_bytes else None

    is_base64_encoded = False  # Cambia a True si decides codificar el body en base64

    headers = dict(request.headers)
    cookies = request.cookies

    query_params = dict(request.query_params)

    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": request.url.path,
        "rawQueryString": request.url.query,
        "cookies": list(cookies.values()) if cookies else [],
        "headers": headers,
        "queryStringParameters": query_params if query_params else None,
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "authentication": {
                "clientCert": {
                    "clientCertPem": "CERT_CONTENT",
                    "subjectDN": "www.example.com",
                    "issuerDN": "Example issuer",
                    "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                    "validity": {
                        "notBefore": "May 28 12:30:02 2019 GMT",
                        "notAfter": "Aug  5 09:36:04 2021 GMT"
                    }
                }
            },
            "authorizer": {
                "jwt": {
                    "claims": {
                        "claim1": "value1",
                        "claim2": "value2"
                    },
                    "scopes": [
                        "scope1",
                        "scope2"
                    ]
                }
            },
            "domainName": "id.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "id",
            "http": {
                "method": request.method,
                "path": request.url.path,
                "protocol": request.scope.get("http_version", "HTTP/1.1"),
                "sourceIp": request.client.host if request.client else "127.0.0.1",
                "userAgent": headers.get("user-agent", "")
            },
            "requestId": str(uuid.uuid4()),
            "routeKey": "$default",
            "stage": "$default",
            "time": datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S +0000"),
            "timeEpoch": int(datetime.utcnow().timestamp() * 1000)
        },
        "body": body_str,
        "pathParameters": path_parameters,
        "isBase64Encoded": is_base64_encoded
    }

from src.lambdas.hello_world.lambda_function import lambda_handler as hello_world_handler
from src.lambdas.prueba.lambda_function import lambda_handler as prueba_handler

router = APIRouter()

@router.get("/hello-world")
async def hello_world(request: Request, response: Response):
    event = await build_event_from_request(request)
    res = hello_world_handler(event, MockContext())
    response.status_code = get_status_code(res)
    return get_body(res)

@router.get("/my-test")
async def prueba(request: Request, response: Response):
    event = await build_event_from_request(request)
    res = prueba_handler(event, MockContext())
    response.status_code = get_status_code(res)
    return get_body(res)

    