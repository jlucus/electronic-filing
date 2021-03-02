from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

def make_custom_openapi(app):

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        securitySchemes = {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }

        router_authorize = [route for route in app.routes[4:] if route.operation_id != "noauth"]

        for route in app.routes:
            if isinstance(route, APIRoute) and route.operation_id == "noauth":
                route.operation_id = route.name

        openapi_schema = get_openapi(
            title="eFile-SD",
            version="3.0.2",
            description="OpenAPI Schema for eFile-SD",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = securitySchemes

        for route in router_authorize:
            for method in list(route.methods):
                method = method.lower()
                security = { 'bearerAuth': [] }
                openapi_schema["paths"][route.path][method]['security'] = [security]
        

        app.openapi_schema = openapi_schema
        return app.openapi_schema


    return custom_openapi
