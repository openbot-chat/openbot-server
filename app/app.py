import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config import ENV
from api.middlewares import AuthMiddleware, TraceMiddleware
# from fastapi_pagination import add_pagination
from handlers import create_start_app_handler, create_stop_app_handler
import otel


def get_application() -> FastAPI:
    app = FastAPI(
        title = os.getenv('api_title', "Openbot"),
        description= os.getenv("api_description", ""),
        contact={
            "name": os.getenv('api_contact_name', 'api'),
            "url": os.getenv('api_contact_url', 'https://twitter.com/openbot_service'),
            "email": os.getenv('api_contact_email', 'api@openbot.com'),
        },
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

    app.add_middleware(
        AuthMiddleware,
    )

    app.add_middleware(
        CORSMiddleware,
        # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
        allow_origins=["*"],
        # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
        allow_credentials=False,
        # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
        allow_methods=["*"],
        # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
        # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
        allow_headers=["*"],
        # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
        # expose_headers=["*"]
        # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
        # max_age=1000
    )

    app.add_middleware(
        TraceMiddleware,
    )

    from api.admin.v1 import api_router as admin_router
    app.include_router(admin_router, dependencies=[])

    from api.openapi.v1 import api_router as openapi_router
    app.include_router(openapi_router, dependencies=[])

    from api.web.v1 import api_router as web_router
    app.include_router(web_router, dependencies=[])

    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    return app


app = get_application()
# add_pagination(app) 不需要在这里集中设置了，repository里头强型设置了 CursorPage

if ENV != "development":
    from otel import (
        setup_instrumentation,
        setup_opentelemetry,
        tracer,
        meter,
    )
    setup_instrumentation(app) 
    setup_opentelemetry(tracer, meter)


@app.get('/health', status_code=200)
def health():
    return "ok"