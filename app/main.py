from fastapi.applications import FastAPI
from starlette.routing import BaseRoute
from app.base.logger import logger as _logger
from app.base.api_init import FastAPIWrapper

from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException

# Initialize the wrapper
wrapper = FastAPIWrapper()
app: FastAPI = wrapper.fastapi_app  

loaded_modules = wrapper.modules
available_modules = wrapper.modules 

@app.get("/", response_class=HTMLResponse)
def root():
    """
    Root get will return a basic website to serve the auto generated docs
    """
    return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>API</title>
                <!-- Include Bootstrap CSS from CDN -->
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            </head>
            <body class="bg-light">
                <div class="container py-5">
                    <h1 class="display-4 text-center mb-3">Welcome the API interface</h1>
                    <p class="lead text-center mb-5">Use the links below to navigate to the API documentation:</p>
                    <div class="row">
                        <div class="col-md-6 text-center mb-3">
                            <a href="/docs" class="btn btn-primary btn-lg">Swagger UI Documentation</a>
                        </div>
                        <div class="col-md-6 text-center mb-3">
                            <a href="/redoc" class="btn btn-secondary btn-lg">ReDoc Documentation</a>
                        </div>
                    </div>
                </div>
                <!-- jQuery first, then Popper.js, then Bootstrap JS -->
                <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            </body>
            </html>
    """

@app.delete("/remove-route")
async def remove_route(path: str):
    route_to_remove = None
    for route in app.router.routes:
        if getattr(route, "path", None) == path:
            route_to_remove: BaseRoute = route
            break
    
    if not route_to_remove:
        raise HTTPException(status_code=404, detail="Route not found")
    
    app.router.routes.remove(route_to_remove)
    app.openapi_schema = None  # Clear the cached schema
    return {"message": f"Route '{path}' has been removed"}


@app.get("/routes/reload-docs")
async def reload_docs():
    app.openapi_schema = None  # Clear the cached schema
    return {"message": "OpenAPI schema reloaded"}


@app.get("/routes")
async def get_active_routes():
    return [route.path for route in app.router.routes]


@app.get("/module/get_loaded_modules")
async def get_loaded_modules() -> list:
    return loaded_modules