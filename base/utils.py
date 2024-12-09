from fastapi import FastAPI, HTTPException, Depends, Request
import importlib
import sys
import os

from .logger import logger as _logger

    
async def log_request_info(request: Request):
    _logger.debug(
        f"{request.method} request to {request.url} metadata\n"
        f"\tHeaders: {request.headers}\n"
        f"\tPath Params: {request.path_params}\n"
        f"\tQuery Params: {request.query_params}\n"
        f"\tCookies: {request.cookies}\n"
    )

def include_router_from_module(app : FastAPI, module_name: str):
    """
    Import module and check if it contains 'router' attribute.
    if it does include the route in the fastapi app 
    """
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'router') and hasattr(module, 'dependency'):
            app.include_router(
                router=module.router,
                dependencies=module.dependency.append(
                    Depends(dependency=log_request_info),
                )
            )
            _logger.info(f"Registered router from module: {module_name} and dependency {module.dependency}")
    except ModuleNotFoundError as e:
        _logger.info(f"Module not found: {module_name}, error: {e}")
    except AttributeError as e:
        _logger.info(f"Module '{module_name}' does not have 'router' attribute, error: {e}")
    except Exception as e:
        _logger.error(f"Module '{module_name}' failed with the following error: {e}")

def register_routes(app : FastAPI):
    """
        Loop a dir for all python files in addons/ dir, 
        and run include_router_from_module()
    """
    addons_dir = os.path.join(os.path.dirname(__file__), '../addons')
    base_module = 'addons'

    for root, dirs, files in os.walk(addons_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                relative_path = os.path.relpath(os.path.join(root, file), addons_dir)
                module_name = os.path.join(base_module, relative_path).replace(os.sep, '.')[:-3]
                include_router_from_module(app=app, module_name=module_name)
