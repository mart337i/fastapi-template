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
from app.base.routing_utils.routing import Routing
# from app.base.db import get_session

# Miscellaneous
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()

class FastAPIWrapper:

    def __init__(self):
        self.sys_modules = sys.modules or {}
        self.routing = Routing()
        self.fastapi_app = self.create_app() # fastapi_app has to be the last to be created


    def load_env(self):
        """
        Loads every config file inside config/ in to the environment
        """
        addons_dir = os.path.join(os.path.dirname(__file__), '../')
        for root, dirs, files in os.walk(addons_dir):
            if 'tests' in dirs:
                _logger.debug(f"Skipped test dir: {os.path.join(root, 'tests')}")
                dirs.remove('tests')  # Prevent descending into 'tests' directories

            if os.path.basename(root) == 'config':
                _logger.debug(f"Inspecting 'config' folder: {root}")
                
                # Find all *.env files in this folder
                for file in files:
                    if file.endswith('.env'):
                        env_file_path = os.path.join(root, file)
                        _logger.info(f"Found .env file: {env_file_path}")


    def create_app(self):
        description = f"API"
        fastapi_app = FastAPI(
            title="API",
            openapi_url=f"/openapi.json",
            docs_url="/docs/",
            description=description,
        )
        self.load_env()

        self.setup_base_routes(app=fastapi_app)
        self.setup_addon_routers(app=fastapi_app)

        self.use_route_names_as_operation_ids(app=fastapi_app)

        self.setup_middleware(app=fastapi_app)
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
        self.routing.register_routes(app=app)


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

