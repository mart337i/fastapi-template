from fastapi.applications import FastAPI
from starlette.routing import BaseRoute
from app.base.logger import logger as _logger
from app.base.api_init import FastAPIWrapper

from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from fastapi.routing import APIRoute

# Initialize the wrapper
wrapper = FastAPIWrapper()
app: FastAPI = wrapper.fastapi_app  

loaded_modules = wrapper.modules
available_modules = wrapper.modules 
deactivated = []

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


@app.delete("/remove-module")
async def remove_module(module_name: str):
    """
    Remove all routes associated with the specified module.

    Args:
        module_name (str): The name of the module whose routes should be removed.

    Returns:
        dict: Confirmation message of the removal process.
    """
    # Find the module
    module_to_remove = next((module for module in loaded_modules if module["name"] == module_name), None)
    if not module_to_remove:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    routes_to_remove = module_to_remove["routes"]
    removed_routes = []
    unmatched_routes = []

    for route_entry in routes_to_remove:
        # Extract the key and value for each route entry
        if len(route_entry) != 1:
            unmatched_routes.append(route_entry)
            continue

        route_path, route_details = next(iter(route_entry.items()))

        # Ensure the route details contain the path and methods
        module_path = route_details.get("path")
        module_methods = eval(route_details.get("methods", "[]"))  # Safely evaluate the set

        if not module_path or not module_methods:
            unmatched_routes.append(route_entry)
            continue

        # Look for a matching route in app.router.routes
        route_to_remove = next(
            (
                route
                for route in app.router.routes
                if isinstance(route, APIRoute)
                and route.path == module_path
                and module_methods.issubset(route.methods)
            ),
            None,
        )

        if route_to_remove:
            app.router.routes.remove(route_to_remove)
            deactivated.append(module_path)
            removed_routes.append(module_path)
        else:
            unmatched_routes.append(route_entry)

    # Clear OpenAPI cache
    app.openapi_schema = None

    return {
        "message": f"Routes from module '{module_name}' have been removed",
        "removed_routes": removed_routes,
        "unmatched_routes": unmatched_routes,
        "app.router.routes": [
            {"path": route.path, "methods": list(route.methods), "name": route.name}
            for route in app.router.routes
            if isinstance(route, APIRoute)
        ],
    }

@app.post("/enable-module")
async def enable_module(module_name: str):
    # Find the module by name
    module_to_enable = next((module for module in loaded_modules if module["name"] == module_name), None)
    if not module_to_enable:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    routes_to_add = module_to_enable["routes"]
    added_routes = []
    skipped_routes = []

    for route_entry in routes_to_add:
        # Extract the route path and its details
        if len(route_entry) != 1:
            skipped_routes.append(route_entry)
            continue

        route_path, route_details = next(iter(route_entry.items()))

        # Parse route details
        path = route_details.get("path")
        methods = eval(route_details.get("methods", "set()"))
        name = route_details.get("name")

        if not path or not methods:
            skipped_routes.append(route_entry)
            continue

        # Debugging existing routes
        _logger.debug(f"Checking if route '{path}' with methods {methods} exists.")

        # Check if the route already exists in app.router.routes
        existing_route = next(
            (
                route
                for route in app.router.routes
                if isinstance(route, APIRoute)
                and route.path == path
                and methods.issubset(route.methods)
            ),
            None,
        )

        if existing_route:
            _logger.warning(f"Route '{path}' already exists, skipping addition.")
            skipped_routes.append(route_entry)
            continue

        # Add the route dynamically
        async def dynamic_handler(request):
            return JSONResponse(content={"message": f"Handled by dynamic route: {path}"})

        _logger.debug(f"Adding route '{path}' with methods {methods}.")
        app.router.add_api_route(
            path=path,
            endpoint=dynamic_handler,
            methods=methods,
            name=name
        )
        added_routes.append(path)

    # Clear OpenAPI schema cache
    app.openapi_schema = None

    return {
        "message": f"Routes for module '{module_name}' have been enabled",
        "added_routes": added_routes,
        "skipped_routes": skipped_routes,
        "app.router.routes": [
            {"path": route.path, "methods": list(route.methods), "name": route.name}
            for route in app.router.routes
            if isinstance(route, APIRoute)
        ],
    }


@app.get("/routes/reload-docs")
async def reload_docs():
    app.openapi_schema = None  # Clear the cached schema
    return {"message": "OpenAPI schema reloaded"}

@app.get("/module/get_loaded_modules")
async def get_loaded_modules() -> list:
    return loaded_modules

@app.get("/module/get_module")
async def get_module(name : str):
    if len([module for module in loaded_modules if module['name'] == name]) != 0:
        return [module for module in loaded_modules if module['name'] == name][0]
    raise HTTPException(status_code=404, detail="Module not found")
    