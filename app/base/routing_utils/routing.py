# Standard library imports
import os
import importlib
import sys

# Third-party imports
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException,APIRouter
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

# Local application imports
from app.base.logger import logger as _logger
from app.base.auth.auth import router as authService
from app.base.utils import log_request_info
from app.base.module import Module
# from app.base.db import get_session

import ast

class Routing():

    def __init__(self):
        self.modules = []


    def register_routes(self,app: FastAPI):
        """
        Loop through all Python files in the addons/ directory, load each module's manifest,
        and register routes in the FastAPI app.
        """
        addons_dir = os.path.join(os.path.dirname(__file__), '../../addons')
        base_module = 'addons'
        for root, dirs, files in os.walk(addons_dir):
            if 'tests' in dirs:
                _logger.info(f"Skipped test dir: {os.path.join(root, 'tests')}")
                dirs.remove('tests')
            if 'config' in dirs:
                _logger.info(f"Skipped config dir: {os.path.join(root, 'tests')}")
                dirs.remove('config')
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_path = os.path.join(root, file)
                    module_name = os.path.relpath(module_path, addons_dir).replace(os.sep, '.').rstrip('.py')
                    # Create a Module instance
                    module = Module(root)
                    try:
                        # Load the module's manifest
                        manifest = module.load_manifest(module_name)
                        if not manifest.get("installable", True):
                            _logger.info(f"Skipping non-installable module: {module_name}")
                            continue
                        # Import the module dynamically
                        spec = importlib.util.spec_from_file_location(f"{base_module}.{module_name}", module_path)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        # Check for and register the router
                        if hasattr(mod, 'router') and hasattr(mod, 'dependency'):
                            if isinstance(mod.router, APIRouter):
                                app.include_router(
                                    router=mod.router,
                                    dependencies=mod.dependency + [
                                        Depends(log_request_info),
                                        # Depends(get_session),
                                    ],
                                )
                                for route in mod.router.routes:
                                    manifest['routes'].append({
                                        route.path : {
                                            'path' : str(route.path),
                                            'name' : str(route.name),
                                            'methods' : str(route.methods),
                                        }
                                })
                                self.modules.append(manifest)
                                _logger.info(f"Registered router from module: {module_name} with dependencies {mod.dependency}")
                            else:
                                _logger.error(f"Imported route is not of type {mod.router} != {APIRouter}")
                        else:
                            _logger.warning(f"Module '{module_name}' does not have 'router' or 'dependency' attributes.")
                    except ModuleNotFoundError as e:
                        _logger.error(f"Module not found: {module_name}, error: {e}")
                    except AttributeError as e:
                        _logger.error(f"Error in module '{module_name}': {e}")
                    except Exception as e:
                        _logger.error(f"Error loading module '{module_name}': {e}")


    def enable_module(self, app: FastAPI, base_module: str):
        """
        Dynamically import and register routes from Python modules in the specified base folder.
        Args:
            app (FastAPI): The FastAPI application instance.
            base_module (str): The Python import base path for the modules.
        """
        addons_dir = os.path.join(os.path.dirname(__file__), '../../addons')
        for root, dirs, files in os.walk(addons_dir):
            # Skip 'tests' and 'config' directories
            if 'tests' in dirs:
                _logger.debug(f"Skipped test dir: {os.path.join(root, 'tests')}")
                dirs.remove('tests')
            if 'config' in dirs:
                _logger.debug(f"Skipped config dir: {os.path.join(root, 'config')}")
                dirs.remove('config')
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_path = os.path.join(root, file)
                    module_name = os.path.relpath(module_path, addons_dir).replace(os.sep, '.').rstrip('.py')
                    try:
                        # Dynamically import the module
                        spec = importlib.util.spec_from_file_location(f"{base_module}.{module_name}", module_path)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        # Load and validate the router
                        if hasattr(mod, 'router') and hasattr(mod, 'dependency'):
                            if isinstance(mod.router, APIRouter):
                                app.include_router(
                                    router=mod.router,
                                    dependencies=mod.dependency + [
                                        Depends(log_request_info),
                                    ],
                                )
                                for route in mod.router.routes:
                                    self.modules.append({
                                        'module': module_name,
                                        'route': {
                                            'path': str(route.path),
                                            'name': str(route.name),
                                            'methods': str(route.methods),
                                        },
                                    })
                                _logger.info(f"Registered router from module: {module_name}")
                            else:
                                _logger.error(f"Router is not of type APIRouter in module: {module_name}")
                        else:
                            _logger.warning(f"Module '{module_name}' does not have 'router' or 'dependency' attributes.")
                    except ModuleNotFoundError as e:
                        _logger.error(f"Module not found: {module_name}, error: {e}")
                    except AttributeError as e:
                        _logger.error(f"Error in module '{module_name}': {e}")
                    except Exception as e:
                        _logger.error(f"Error loading module '{module_name}': {e}")



    def remove_module(self, app: FastAPI, base_module: str, loaded_modules):
        addons_dir = os.path.join(os.path.dirname(__file__), '../../addons')

        # Find the module by technical_name
        module_to_remove = next((module for module in loaded_modules if base_module == module['technical_name']), None)
        if not module_to_remove:
            raise HTTPException(status_code=404, detail=f"Module '{base_module}' not found")

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
            
            # Safely convert methods to a set
            try:
                module_methods = ast.literal_eval(route_details.get("methods", "[]"))  # Convert string to set
                if not isinstance(module_methods, set):  # Ensure it's a set
                    module_methods = set(module_methods)
            except (ValueError, SyntaxError):
                unmatched_routes.append(route_entry)
                continue

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
                removed_routes.append(module_path)
            else:
                unmatched_routes.append(route_entry)

        # Clear OpenAPI schema cache to reflect the removed routes
        app.openapi_schema = None

        return {
            "message": f"Routes from module '{base_module}' have been removed",
            "removed_routes": removed_routes,
            "unmatched_routes": unmatched_routes,
        }
