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

loaded_modules = wrapper.routing.modules
available_modules = wrapper.routing.modules
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
async def remove_module(technical_name: str):
    """
    Remove all routes associated with the specified module.

    Args:
        technical_name (str): The name of the module whose routes should be removed.

    Returns:
        dict: Confirmation message of the removal process.
    """
    try:
        _logger.info(f"Remove module from technical_name: {technical_name}")
        rec = wrapper.routing.remove_module(app, technical_name,loaded_modules)
        app.openapi_schema = None

        return rec
    except Exception as e:
        _logger.error(f"Failed to remove module at '{technical_name}': {e}")
        return {"status": "error", "message": str(e)}


@app.post("/enable-module")
def enable_module(technical_name: str):
    """
    Enable and register routes for a specific module located at the given technical_name.

    Args:
        technical_name (str): The technical_name to the module folder.
    """
    try:
        _logger.info(f"Enabling module from technical_name: {technical_name}")
        wrapper.routing.enable_module(app, technical_name)
        app.openapi_schema = None

        return {"status": "success", "message": f"Module at '{technical_name}' has been enabled."}
    except Exception as e:
        _logger.error(f"Failed to enable module at '{technical_name}': {e}")
        return {"status": "error", "message": str(e)}

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
    