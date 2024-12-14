# Standard library imports
import os
import importlib
import sys

# Third-party imports
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

# Local application imports
from app.base.logger import logger as _logger
from app.base.routing.auth import router as authService
from app.base.utils import log_request_info
from app.base.module import Module

# Miscellaneous
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()

class FastAPIWrapper:

    def __init__(self):
        self.modules = []
        self.sys_modules = sys.modules or {}
        self.fastapi_app = self.create_app()


    def load_env(self):
        """
        Loads every config file inside config/ in to the environment
        """
        dirname = os.path.dirname(__file__)
        config_dir = os.path.join(dirname, 'config')

        for config_file in os.listdir(path=config_dir):
            config_path = os.path.join(config_dir, config_file)
            if os.path.isfile(path=config_path):
                load_dotenv(dotenv_path=config_path, override=True)


    def create_app(self):
        description = f"API"
        fastapi_app = FastAPI(
            title="API",
            openapi_url=f"/openapi.json",
            docs_url="/docs/",
            description=description,
        )
        self.setup_base_routes(app=fastapi_app)
        self.setup_addon_routers(app=fastapi_app)

        self.use_route_names_as_operation_ids(app=fastapi_app)

        self.setup_middleware(app=fastapi_app)
        self.load_env()
        return fastapi_app

    def setup_base_routes(self,app: FastAPI) -> None:
        # Base Routes 
        app.include_router(
            router=authService,
            prefix=f"/auth",
            tags=["Authentication Service"],
        )

    def setup_addon_routers(self,app: FastAPI) -> None:
        """
            Import all routes using dynamic importing (Reflections)
        """
        self.register_routes(app=app)


    def setup_middleware(self,app : FastAPI):
        origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:8080",
        ]

        app.add_middleware(
            middleware_class=CORSMiddleware,
            allow_credentials=True,
            allow_origins=origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # app.add_middleware(
        #     # Ensures all trafic to server is ssl encrypted or is rederected to https / wss
        #     middleware_class=HTTPSRedirectMiddleware
        # )

    def use_route_names_as_operation_ids(self,app: FastAPI) -> None:
        """
        Simplify operation IDs so that generated API clients have simpler function
        names.

        Should be called only after all routes have been added.
        """
        route_names = set()
        for route in app.routes:
            if isinstance(route, APIRoute):
                if route.name in route_names:
                    raise Exception(f"Route function names {[route.name]} should be unique")
                route.operation_id = route.name
                route_names.add(route.name)


    def register_routes(self, app: FastAPI):
        """
        Loop through all Python files in the addons/ directory, load each module's manifest,
        and register routes in the FastAPI app.
        """
        addons_dir = os.path.join(os.path.dirname(__file__), '../addons')
        base_module = 'addons'

        for root, dirs, files in os.walk(addons_dir):
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
                            app.include_router(
                                router=mod.router,
                                dependencies=mod.dependency + [
                                    Depends(log_request_info)
                                ],
                            )
                            self.modules.append(manifest)
                            _logger.info(f"Registered router from module: {module_name} with dependencies {mod.dependency}")
                        else:
                            _logger.info(f"Module '{module_name}' does not have 'router' or 'dependency' attributes.")

                    except ModuleNotFoundError as e:
                        _logger.error(f"Module not found: {module_name}, error: {e}")
                    except AttributeError as e:
                        _logger.error(f"Error in module '{module_name}': {e}")
                    except Exception as e:
                        _logger.error(f"Error loading module '{module_name}': {e}")


