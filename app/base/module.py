import os
import sys
import importlib
import re
import copy
import ast
from os.path import join as opj, normpath
import logging

MANIFEST_NAMES = ["__manifest__.py"]
README_NAMES = ["README.md", "README.rst"]
_DEFAULT_MANIFEST = {}

_logger = logging.getLogger(__name__)

class Module:
    def __init__(self, module_path: str):
        self.module_path = module_path
        self.manifest = {}
        self.name = False
        

    def load_module(self, name):
        assert name not in sys.modules

        mod = importlib.import_module(name)
        sys.modules[name] = mod
        return sys.modules[name]

    def module_manifest(self, path):
        """Returns path to module manifest if one can be found under `path`, else `None`."""
        if not path:
            return None
        for manifest_name in MANIFEST_NAMES:
            candidate = opj(path, manifest_name)
            if os.path.isfile(candidate):
                return candidate

    def get_module_root(self, path):
        """
        Get closest module's root beginning from path

        # Given:
        # /foo/bar/module_dir/static/src/...

        get_module_root('/foo/bar/module_dir/static/')
        # returns '/foo/bar/module_dir'

        get_module_root('/foo/bar/module_dir/')
        # returns '/foo/bar/module_dir'

        get_module_root('/foo/bar')
        # returns None

        @param path: Path from which the lookup should start

        @return:  Module root path or None if not found
        """
        while not self.module_manifest(path):
            new_path = os.path.abspath(opj(path, os.pardir))
            if path == new_path:
                return None
            path = new_path
        return path

    def adapt_version(self, version):
        example = "1.0.0"
        if not re.match(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$", version):
            raise ValueError(f"Invalid version {version!r}. Modules should have a version in format `x.y`, `x.y.z`,"
                             f" `{example}.x.y` or `{example}.x.y.z`."
                            )

        return version

    def load_manifest(self, module, mod_path=None):
        """ Load the module manifest from the file system. """

        if not mod_path:
            mod_path = self.get_module_root(self.module_path)

        manifest_file = self.module_manifest(mod_path)

        if not manifest_file:
            _logger.debug('module %s: no manifest file found %s', module, MANIFEST_NAMES)
            return {}

        manifest = copy.deepcopy(_DEFAULT_MANIFEST)

        try:
            with open(manifest_file, 'r') as f:
                manifest.update(ast.literal_eval(f.read()))
        except FileNotFoundError:
            _logger.error("Manifest file not found: %s", manifest_file)
            return {}
        except Exception as e:
            _logger.error("Error reading manifest file %s: %s", manifest_file, e)
            return {}

        if not manifest['description']:
            readme_path = [opj(mod_path, x) for x in README_NAMES
                           if os.path.isfile(opj(mod_path, x))]
            if readme_path:
                try:
                    with open(readme_path[0], 'r') as fd:
                        manifest['description'] = fd.read()
                except Exception as e:
                    _logger.error("Error reading README file %s: %s", readme_path[0], e)

        if not manifest.get('license'):
            manifest['license'] = 'LGPL-3'
            _logger.warning("Missing `license` key in manifest for %r, defaulting to LGPL-3", module)

        try:
            manifest['version'] = self.adapt_version(manifest['version'])
        except ValueError as e:
            if manifest.get("installable", True):
                raise ValueError(f"Module {module}: invalid manifest") from e
        
        if not manifest.get('routes'):
            manifest['routes'] = []

        manifest['addons_path'] = normpath(opj(mod_path, os.pardir))
        return manifest