"""Transactional, replayable commissioning state using only Python and SQLite.

The journal proves internal consistency and captured-byte integrity. It is not a
signature, an external truth oracle, or protection from an administrator replacing
the entire database and recomputing its chain. See docs/BOOTSTRAP_RUNTIME.md.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import sqlite3
import stat
import sys
import threading
import types
import uuid

from . import __version__

SCHEMA_VERSION = 2
MAX_ARTIFACT_BYTES = 8 * 1024 * 1024
MAX_CAPTURE_BYTES = 32 * 1024 * 1024
MAX_REQUEST_BYTES = 64 * 1024
MAX_RESULT_BYTES = 4 * 1024 * 1024
MAX_CONTEXT_FILE_BYTES = 2 * 1024 * 1024
MAX_CONTEXT_BYTES = 8 * 1024 * 1024
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_REGISTRIES = (
    ("constitution", "registry/constitution.json", True),
    ("source-manifest", "registry/sources.json", True),
    ("authority", "registry/authority.json", True),
    ("repository-pins", "registry/repositories.json", False),
    ("inherited-obligations", "registry/inherited_obligations.json", False),
)
CONTEXT_CODE = tuple(("runtime-source", f"polyia/{name}.py", True)
                     for name in ("__init__", "store", "experiments", "cli", "server", "__main__"))
COMMANDS = frozenset({"guidance.submit", "guidance.ack", "guidance.apply",
                      "requirement.produce", "requirement.verify", "requirement.accept",
                      "checkpoint.create", "experiment.run"})
REGISTERED_EXPERIMENTS = frozenset({"polynomial", "grammar-promotion", "qpath", "acceptance", "native", "intake", "astra", "rasm", "forms", "generators"})
# Versioned historical bundle contracts: do not expand these in place. A future
# dependency closure uses a new bundle version so prior journal records remain valid.
_EXTENSION_DEPENDENCIES_V1 = {
    "native": ("polyia.capabilities", "polyia.native"),
    "intake": ("polyia.capabilities", "polyia.intake", "polyia.experiments", "polyia.native"),
    "astra": ("polyia.capabilities", "polyia.astra"),
    "rasm": ("polyia.capabilities", "polyia.rasm"),
    "forms": ("polyia.capabilities", "polyia.forms"),
    "generators": ("polyia.capabilities", "polyia.generators"),
}
_EXTENSION_ENTRYPOINTS = {
    "polyia.capabilities": ("run_registered",),
    "polyia.native": ("compile_program", "execute_program"),
    "polyia.intake": ("run_intake",),
    "polyia.astra": ("run_adapter",),
    "polyia.rasm": ("run_rasm",),
    "polyia.forms": ("run_forms",),
    "polyia.generators": ("compile_model", "run_model", "render_explanation", "build_curriculum"),
}
_EXTENSION_PINS = {}
LEDGER_TABLES = frozenset({"genesis", "materialized", "events", "receipts", "blobs", "checkpoints", "refusals"})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SCIENCE_PIN_LOCK = threading.RLock()
_SCIENCE_PIN = None


class CommandError(Exception):
    """A refused command or an explicitly unavailable/corrupt runtime."""

    def __init__(self, code, message, http_status=400, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details

    def as_dict(self):
        result = {"code": self.code, "message": self.message}
        if self.details is not None:
            result["details"] = self.details
        return result


def _json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(value):
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _same_json(left, right):
    """JSON identity is type-sensitive: true, 1, and 1.0 are distinct."""
    return _json(left) == _json(right)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _fail(code, message, status=400, details=None):
    raise CommandError(code, message, status, details)


def _text(value, name, *, maximum=4000, empty=False):
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()):
        _fail("INVALID_PAYLOAD", f"{name} must be a {'possibly empty ' if empty else 'nonempty '}string of at most {maximum} characters")
    return value


def _keys(payload, required, optional=()):
    if not isinstance(payload, dict) or set(payload) - set(required) - set(optional) or set(required) - set(payload):
        _fail("INVALID_PAYLOAD", "Payload fields do not match the registered command schema",
              details={"required": sorted(required), "optional": sorted(optional)})


def _code_identity(module_name):
    if module_name == "polyia.experiments":
        return _pinned_science()[1]
    module = importlib.import_module(module_name)
    path = Path(module.__file__)
    return {"module": module_name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "package_version": __version__, "python_version": platform.python_version()}


def _code_structure(code):
    """Stable typed code representation, independent of marshal interning."""
    def constant(value):
        if isinstance(value, types.CodeType):
            return {"type": "code", "value": _code_structure(value)}
        if isinstance(value, tuple):
            return {"type": "tuple", "value": [constant(item) for item in value]}
        if isinstance(value, frozenset):
            return {"type": "frozenset", "value": sorted((constant(item) for item in value), key=_json)}
        return {"type": type(value).__name__, "value": repr(value)}
    return {"bytecode": code.co_code.hex(), "constants": [constant(value) for value in code.co_consts],
            "names": code.co_names, "variables": code.co_varnames, "freevars": code.co_freevars,
            "cellvars": code.co_cellvars, "arguments": [code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount],
            "locals": code.co_nlocals, "stacksize": code.co_stacksize, "flags": code.co_flags,
            "name": code.co_name, "qualname": code.co_qualname, "firstlineno": code.co_firstlineno,
            "linetable": code.co_linetable.hex(), "exceptiontable": code.co_exceptiontable.hex()}


def _science_loaded_functions(module):
    functions = {}
    for value in vars(module).values():
        candidates = vars(value).values() if isinstance(value, type) and value.__module__ == module.__name__ else (value,)
        for candidate in candidates:
            if isinstance(candidate, (staticmethod, classmethod)):
                candidate = candidate.__func__
            if isinstance(candidate, types.FunctionType) and candidate.__module__ == module.__name__:
                function = inspect.unwrap(candidate)
                functions[function.__qualname__] = {
                    "code_sha256": _hash(_code_structure(function.__code__)),
                    "defaults": list(function.__defaults__) if function.__defaults__ is not None else None,
                    "kwdefaults": function.__kwdefaults__,
                }
    return functions


def _pinned_science():
    """Bind bytes to already-loaded registered code; never execute input code.

    Compiling the installed, fixed module here only builds a comparison object.
    No compiled object is evaluated or installed. A cached module whose source
    functions/constants no longer agree is refused, including before first pin.
    """
    global _SCIENCE_PIN
    with _SCIENCE_PIN_LOCK:
        module = importlib.import_module("polyia.experiments")
        path = Path(module.__file__).resolve()
        with path.open("rb") as stream:
            source = stream.read(MAX_CONTEXT_FILE_BYTES + 1)
        if not source or len(source) > MAX_CONTEXT_FILE_BYTES:
            _fail("IMPLEMENTATION_CHANGED", "Scientific source is unavailable or exceeds its pinned-source budget", 409)
        digest = hashlib.sha256(source).hexdigest()
        functions = _science_loaded_functions(module)
        if _SCIENCE_PIN is None:
            tree = ast.parse(source, filename=str(path))
            compiled = compile(source, str(path), "exec", dont_inherit=True, optimize=sys.flags.optimize)
            code_map = {}
            stack = [compiled]
            while stack:
                code = stack.pop()
                code_map[code.co_qualname] = _hash(_code_structure(code))
                stack.extend(value for value in code.co_consts if isinstance(value, types.CodeType))
            expected_names = set()
            expected_defaults = {}
            literals = {}
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    expected_names.add(node.name)
                    function_nodes = [(node.name, node)]
                elif isinstance(node, ast.ClassDef):
                    expected_names.update(node.name + "." + member.name for member in node.body
                                          if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)))
                    function_nodes = [(node.name + "." + member.name, member) for member in node.body
                                      if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))]
                elif isinstance(node, ast.Assign):
                    function_nodes = []
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            try:
                                literal = ast.literal_eval(node.value)
                                _json(literal)
                            except (ValueError, TypeError, SyntaxError):
                                continue
                            literals[target.id] = literal
                else:
                    function_nodes = []
                for name, function_node in function_nodes:
                    try:
                        defaults = [ast.literal_eval(value) for value in function_node.args.defaults] or None
                        kwdefaults = {argument.arg: ast.literal_eval(value)
                                      for argument, value in zip(function_node.args.kwonlyargs, function_node.args.kw_defaults)
                                      if value is not None} or None
                        expected_defaults[name] = {"defaults": defaults, "kwdefaults": kwdefaults}
                        _json(expected_defaults[name])
                    except (ValueError, TypeError, SyntaxError):
                        _fail("IMPLEMENTATION_CHANGED", "Scientific defaults require explicit literal source binding", 409)
            if (set(functions) != expected_names or "run_registered" not in functions
                    or any(functions[name]["code_sha256"] != code_map.get(name) for name in functions)
                    or any(not _same_json({key: functions[name][key] for key in ("defaults", "kwdefaults")},
                                          expected_defaults[name]) for name in functions)
                    or any(not _same_json(getattr(module, name, None), value) for name, value in literals.items())):
                _fail("IMPLEMENTATION_CHANGED", "Loaded scientific code does not match the installed source; restart with a coherent package", 409)
            identity = {"module": "polyia.experiments", "sha256": digest,
                        "loaded_code_sha256": _hash({"functions": functions, "constants": literals}),
                        "package_version": __version__, "python_version": platform.python_version(),
                        "source_binding": "PINNED_SOURCE_MATCHES_LOADED_CODE"}
            _SCIENCE_PIN = {"source": source, "identity": identity, "functions": functions, "constants": literals}
        pin = _SCIENCE_PIN
        if (digest != pin["identity"]["sha256"] or not _same_json(functions, pin["functions"])
                or any(not _same_json(getattr(module, name, None), value) for name, value in pin["constants"].items())):
            _fail("IMPLEMENTATION_CHANGED", "Scientific implementation changed in this process; restart before new scientific evidence", 409)
        return module, deepcopy(pin["identity"]), pin["source"]


def _bound_value(value):
    """Type-preserving immutable snapshots of literal and regex policy values."""
    if isinstance(value, re.Pattern):
        return {"type": "regex", "pattern": value.pattern, "flags": value.flags}
    if type(value) in (str, int, float, bool, type(None)):
        return {"type": type(value).__name__, "value": value}
    if type(value) in (tuple, list):
        return {"type": type(value).__name__, "value": [_bound_value(item) for item in value]}
    if type(value) is dict:
        return {"type": "dict", "value": [[_bound_value(key), _bound_value(item)] for key,item in value.items()]}
    _fail("IMPLEMENTATION_CHANGED", "Unbound extension policy value type", 409)


def _source_constant(node, values):
    """Evaluate only declared constant forms; never evaluate arbitrary source."""
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        pass
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        items = [_source_constant(item, values) for item in node.elts]
        return tuple(items) if isinstance(node, ast.Tuple) else items
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _source_constant(node.left, values), _source_constant(node.right, values)
        if type(left) == type(right) and type(left) in (str, tuple, list):
            return left + right
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "re" and node.attr in ("I", "IGNORECASE", "ASCII"):
        return getattr(re, node.attr)
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "re" and node.func.attr == "compile"
            and not node.keywords and 1 <= len(node.args) <= 2):
        args = [_source_constant(argument, values) for argument in node.args]
        if type(args[0]) is str and (len(args) == 1 or isinstance(args[1], int)):
            return re.compile(*args)
    _fail("IMPLEMENTATION_CHANGED", "Extension constants need an explicitly supported source binding", 409)


def _extension_imports(tree, module):
    """Resolve installed fixed imports, including captured transitive aliases."""
    bindings, descriptions = {}, {}
    stdlib = {"fractions", "hashlib", "json", "re", "copy", "math", "typing", "unicodedata", "itertools"}
    project = set(_EXTENSION_ENTRYPOINTS) | {"polyia.experiments"}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for item in node.names:
                if item.name not in stdlib:
                    _fail("IMPLEMENTATION_CHANGED", "Extension imports an undeclared dependency", 409)
                key = item.asname or item.name
                expected = importlib.import_module(item.name)
                bindings[key], descriptions[key] = expected, item.name
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            for item in node.names:
                key = item.asname or item.name
                if node.level:
                    target = "polyia." + (node.module or item.name)
                    if node.level != 1 or target not in project:
                        _fail("IMPLEMENTATION_CHANGED", "Extension project import is not declared", 409)
                    imported = importlib.import_module(target)
                    expected = imported if node.module is None else getattr(imported, item.name)
                    description = target if node.module is None else target + "." + item.name
                else:
                    if node.module not in stdlib:
                        _fail("IMPLEMENTATION_CHANGED", "Extension imports an undeclared library", 409)
                    expected = getattr(importlib.import_module(node.module), item.name)
                    description = node.module + "." + item.name
                bindings[key], descriptions[key] = expected, description
    if any(getattr(module,key,None) is not value for key,value in bindings.items()):
        _fail("IMPLEMENTATION_CHANGED", "Loaded extension dependency alias differs from its installed import", 409)
    return bindings, descriptions


def _extension_classes(nodes, module):
    """Bind the supported exception/plain/TypedDict declarations as well."""
    result = {}
    bases = {"Exception": Exception, "ValueError": ValueError, "object": object, "TypedDict": dict}
    for node in nodes:
        if (node.decorator_list or node.keywords or len(node.bases) > 1
                or any(not isinstance(base, ast.Name) or base.id not in bases for base in node.bases)):
            _fail("IMPLEMENTATION_CHANGED", "Extension class declaration needs explicit binding", 409)
        expected = (bases[node.bases[0].id],) if node.bases else (object,)
        loaded = getattr(module, node.name, None)
        if not isinstance(loaded, type) or loaded.__module__ != module.__name__ or loaded.__bases__ != expected:
            _fail("IMPLEMENTATION_CHANGED", "Loaded extension class bases differ from source", 409)
        allowed = {"__module__", "__doc__", "__dict__", "__weakref__", "__firstlineno__", "__static_attributes__", "__annotations__"}
        allowed.update(member.name for member in node.body if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)))
        if node.bases and node.bases[0].id == "TypedDict":
            allowed.update({"__orig_bases__", "__required_keys__", "__optional_keys__", "__readonly_keys__", "__mutable_keys__", "__total__"})
        if set(vars(loaded)) - allowed:
            _fail("IMPLEMENTATION_CHANGED", "Loaded extension class has an undeclared runtime hook", 409)
        annotations = {item.target.id: ast.unparse(item.annotation) for item in node.body
                       if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)}
        actual = {key: (value if isinstance(value, str) else getattr(value, "__forward_arg__", getattr(value, "__name__", None)))
                  for key, value in getattr(loaded, "__annotations__", {}).items()}
        if annotations != actual:
            _fail("IMPLEMENTATION_CHANGED", "Loaded extension class annotations differ from source", 409)
        result[node.name] = {"bases": [base.__module__ + "." + base.__qualname__ for base in expected],
                             "annotations": annotations}
    return result


def _pinned_module(module_name):
    """Bind each fixed extension to loaded functions, policies and dependencies.

    Existing seed identity stays on the original pinning algorithm. Extension
    pinning additionally binds derived constants, regex policies and imports.
    Source compilation is comparison only; no compiled object is executed.
    """
    if module_name == "polyia.experiments":
        return _pinned_science()
    if module_name not in _EXTENSION_ENTRYPOINTS:
        _fail("UNSUPPORTED_IMPLEMENTATION", "Module is not in the trusted extension allowlist", 409)
    with _SCIENCE_PIN_LOCK:
        module = importlib.import_module(module_name)
        path = Path(module.__file__).resolve()
        if path != PACKAGE_ROOT / (module_name.replace(".", "/") + ".py"):
            _fail("IMPLEMENTATION_CHANGED", "Extension module is outside its installed package path", 409)
        with path.open("rb") as handle:
            source = handle.read(MAX_CONTEXT_FILE_BYTES + 1)
        if not source or len(source) > MAX_CONTEXT_FILE_BYTES:
            _fail("IMPLEMENTATION_CHANGED", "Extension source exceeds the captured-source budget", 409)
        digest = hashlib.sha256(source).hexdigest()
        functions = _science_loaded_functions(module)
        pin = _EXTENSION_PINS.get(module_name)
        if pin is None:
            tree = ast.parse(source, filename=str(path))
            compiled = compile(source, str(path), "exec", dont_inherit=True, optimize=sys.flags.optimize)
            stack, code_map = [compiled], {}
            while stack:
                code = stack.pop()
                code_map[code.co_qualname] = _hash(_code_structure(code))
                stack.extend(value for value in code.co_consts if isinstance(value, types.CodeType))
            expected, values = {}, {}
            for node in tree.body:
                function_nodes = []
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_nodes = [(node.name,node)]
                elif isinstance(node, ast.ClassDef):
                    function_nodes = [(node.name+"."+member.name,member) for member in node.body
                                      if isinstance(member,(ast.FunctionDef,ast.AsyncFunctionDef))]
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            values[target.id] = _source_constant(node.value,values)
                for name,function_node in function_nodes:
                    try:
                        expected[name] = {
                            "code_sha256": code_map[name],
                            "defaults": [ast.literal_eval(v) for v in function_node.args.defaults] or None,
                            "kwdefaults": {arg.arg: ast.literal_eval(value) for arg,value in zip(function_node.args.kwonlyargs,function_node.args.kw_defaults) if value is not None} or None}
                    except (ValueError,TypeError,SyntaxError,KeyError):
                        _fail("IMPLEMENTATION_CHANGED", "Extension defaults need literal source binding", 409)
            constants = {name:_bound_value(value) for name,value in values.items()}
            if (not _same_json(functions,expected) or not set(_EXTENSION_ENTRYPOINTS[module_name]) <= set(functions)
                    or any(not _same_json(_bound_value(getattr(module,name,None)),value) for name,value in constants.items())):
                _fail("IMPLEMENTATION_CHANGED", "Loaded extension differs from its installed functions or constants", 409)
            imports, descriptions = _extension_imports(tree,module)
            class_nodes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
            classes = _extension_classes(class_nodes, module)
            identity = {"module":module_name,"sha256":digest,
                        "loaded_code_sha256":_hash({"functions":functions,"constants":constants,"imports":descriptions,"classes":classes}),
                        "package_version":__version__,"python_version":platform.python_version(),
                        "source_binding":"PINNED_SOURCE_MATCHES_LOADED_CODE"}
            pin = {"source":source,"identity":identity,"functions":deepcopy(functions),"constants":constants,"imports":imports,
                   "class_nodes":class_nodes,"classes":classes}
            _EXTENSION_PINS[module_name] = pin
        if (digest != pin["identity"]["sha256"] or not _same_json(functions,pin["functions"])
                or any(not _same_json(_bound_value(getattr(module,name,None)),value) for name,value in pin["constants"].items())
                or any(getattr(module,name,None) is not value for name,value in pin["imports"].items())
                or not _same_json(_extension_classes(pin["class_nodes"],module),pin["classes"])):
            _fail("IMPLEMENTATION_CHANGED", "Extension implementation changed; restart with a coherent package", 409)
        # A function copied with different globals or hidden behind __wrapped__
        # does not establish identity merely by preserving its original bytecode.
        for value in vars(module).values():
            candidates = vars(value).values() if isinstance(value,type) and value.__module__ == module_name else (value,)
            for candidate in candidates:
                if isinstance(candidate,(staticmethod,classmethod)): candidate = candidate.__func__
                if isinstance(candidate,types.FunctionType) and candidate.__module__ == module_name:
                    if candidate.__globals__ is not vars(module) or hasattr(candidate,"__wrapped__"):
                        _fail("IMPLEMENTATION_CHANGED", "Extension function globals or wrapper are not source bound", 409)
        return module,deepcopy(pin["identity"]),pin["source"]


def _definitions(requirements):
    if requirements is None:
        path = Path(__file__).resolve().parent.parent / "registry" / "constitution.json"
        if not path.is_file():
            _fail("MISSING_CONSTITUTION", "The default constitution registry is unavailable; provide explicit requirements", 503)
        document = json.loads(path.read_text(encoding="utf-8"))
        requirements = document if isinstance(document, list) else document.get("requirements", document.get("obligations"))
    if not isinstance(requirements, list):
        _fail("INVALID_REQUIREMENTS", "Requirements must be a list")
    normalized = {}
    for item in requirements:
        if not isinstance(item, dict):
            _fail("INVALID_REQUIREMENTS", "Every requirement must be an object")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not _IDENTIFIER.fullmatch(identifier) or identifier in normalized:
            _fail("INVALID_REQUIREMENTS", "Requirement IDs must be unique stable identifiers")
        title, verifier = item.get("title"), item.get("verifier")
        if not isinstance(title, str) or not title.strip() or not isinstance(verifier, str) or not verifier.strip():
            _fail("INVALID_REQUIREMENTS", "Every requirement needs a title and registered verifier name")
        # Scope, mandate, acceptance, authority and source metadata are part of
        # the immutable requirement definition, not expendable UI decoration.
        try:
            normalized[identifier] = json.loads(_json(item))
        except (TypeError, ValueError, RecursionError):
            _fail("INVALID_REQUIREMENTS", "Requirement metadata must be finite JSON data")
    return normalized


def _initial_state(definitions, source_context):
    return {"schema_version": SCHEMA_VERSION, "commission_status": "NOT_COMMISSIONED",
            "requirements": {key: dict(value, status="NOT_STARTED", priority=5, artifacts=[],
                                        verification=None, verification_attempts=[])
                             for key, value in sorted(definitions.items())},
            "guidance": {}, "research": {"paused": False}, "runs": [], "latest_checkpoint": None,
            "source_context": deepcopy(source_context)}


def _reduce(state, event):
    """Pure reducer: consumes recorded results; performs no IO or execution."""
    state = deepcopy(state)
    kind, sequence = event["kind"], event["sequence"]
    request, result = event["payload"]["request"], event["payload"]["result"]
    payload = request["payload"]
    if kind == "guidance.submit":
        guidance_id = result["guidance_id"]
        state["guidance"][guidance_id] = {"id": guidance_id, "target": payload["target"],
            "text": payload["text"], "action": payload.get("action"), "status": "SUBMITTED",
            "submitted_by": event["actor"], "submitted_at": event["timestamp"], "submitted_revision": sequence,
            "acknowledgments": [], "applied_revision": None, "effects": []}
    elif kind == "guidance.ack":
        guidance = state["guidance"][payload["guidance_id"]]
        guidance["status"] = payload["disposition"]
        guidance["acknowledgments"].append({"disposition": payload["disposition"], "reason": payload["reason"],
            "actor": event["actor"], "revision": sequence, "timestamp": event["timestamp"]})
    elif kind == "guidance.apply":
        guidance = state["guidance"][payload["guidance_id"]]
        action = guidance["action"]
        if action["kind"] == "set_priority":
            state["requirements"][action["target"]]["priority"] = action["priority"]
        elif action["kind"] == "pause_research":
            state["research"]["paused"] = True
        elif action["kind"] == "resume_research":
            state["research"]["paused"] = False
        else:
            raise ValueError("Unregistered guidance action in journal")
        guidance.update(status="APPLIED", applied_revision=sequence, applied_by=event["actor"], effects=result["effects"])
    elif kind == "requirement.produce":
        requirement = state["requirements"][payload["requirement_id"]]
        requirement.update(status="PRODUCED", artifacts=result["artifacts"], verification=None,
                           produced_revision=sequence, produced_by=event["actor"], note=payload.get("note", ""))
        requirement.pop("accepted_revision", None)
        requirement.pop("accepted_by", None)
    elif kind == "requirement.verify":
        requirement = state["requirements"][payload["requirement_id"]]
        verification = result["verification"]
        requirement["verification"] = verification
        requirement["verification_attempts"].append(verification)
        requirement["status"] = "VERIFIED" if verification["outcome"] == "PASS" else "PRODUCED"
        requirement.pop("accepted_revision", None)
        requirement.pop("accepted_by", None)
    elif kind == "requirement.accept":
        state["requirements"][payload["requirement_id"]].update(status="ACCEPTED", accepted_revision=sequence,
                                                               accepted_by=event["actor"])
    elif kind == "checkpoint.create":
        state["source_context"] = result["source_context"]
        state["latest_checkpoint"] = {"id": result["checkpoint_id"], "revision": sequence,
                                      "note": payload.get("note", ""), "previous_id": result["previous_id"]}
    elif kind == "experiment.run":
        state["runs"].append(result["run"])
    else:
        raise ValueError("Unregistered journal event")
    return state


class Ledger:
    """Durable state owner. Each new command is a serialized SQLite transaction."""

    def __init__(self, db_path, workspace, requirements=None):
        self.db_path = Path(db_path).expanduser().resolve()
        self.workspace = Path(workspace).expanduser().resolve(strict=True)
        if not self.workspace.is_dir():
            _fail("INVALID_WORKSPACE", "Workspace must be an existing directory")
        self.db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._closed = False
        self._conn = sqlite3.connect(str(self.db_path), isolation_level=None, timeout=15,
                                     check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        try:
            os.chmod(self.db_path, 0o600)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=FULL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.execute("PRAGMA busy_timeout=15000")
            with self._transaction():
                existing = {row[0] for row in self._conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if existing and not LEDGER_TABLES <= existing:
                    _fail("INTEGRITY_ERROR", "Database is missing required ledger tables; no schema repair was attempted", 409,
                          {"missing_tables": sorted(LEDGER_TABLES - existing)})
                if not existing:
                    self._schema()
                row = self._conn.execute("SELECT * FROM genesis WHERE singleton=1").fetchone()
                if row is None:
                    if existing:
                        _fail("INTEGRITY_ERROR", "Existing ledger has no genesis record", 409)
                    definitions = _definitions(requirements)
                    self._context_mode = "package" if requirements is None else "workspace"
                    self._genesis_definitions_hash = _hash(definitions)
                    timestamp = _now()
                    context = self._capture_source_context(1, 0, timestamp)
                    if requirements is None and context["definition_binding"]["status"] != "MATCH":
                        _fail("SOURCE_CONTEXT_CHANGED", "The packaged constitution changed while genesis was being captured", 409)
                    state = _initial_state(definitions, context)
                    genesis = {"schema_version": SCHEMA_VERSION, "timestamp": timestamp,
                               "runtime_version": __version__, "definitions": definitions, "state": state,
                               "context_mode": self._context_mode, "source_context": context}
                    head = _hash(genesis)
                    self._conn.execute("INSERT INTO genesis VALUES (1, ?, ?)", (_json(genesis), head))
                    self._conn.execute("INSERT INTO materialized VALUES (1, ?, ?, 0, ?)", (_json(state), _hash(state), head))
                else:
                    stored = json.loads(row["document_json"])
                    self._context_mode = stored.get("context_mode")
                    self._genesis_definitions_hash = _hash(stored["definitions"])
                    if requirements is not None and not _same_json(_definitions(requirements), stored["definitions"]):
                        _fail("CONFIGURATION_CONFLICT", "Existing genesis requirements differ from the supplied definitions", 409)
                report = self._verify_locked()
                if not report["ok"]:
                    _fail("INTEGRITY_ERROR", "Ledger verification failed on open; no repair was attempted", 409, report)
        except BaseException as error:
            self._conn.close()
            self._closed = True
            if isinstance(error, (sqlite3.DatabaseError, ValueError, TypeError, KeyError, RecursionError)):
                raise CommandError("INTEGRITY_ERROR", "Ledger could not be opened consistently; no repair was attempted", 409,
                                   {"reason": str(error)[:1000]}) from error
            raise

    def _schema(self):
        schema = """
            CREATE TABLE IF NOT EXISTS genesis (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1), document_json TEXT NOT NULL, digest TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS materialized (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1), state_json TEXT NOT NULL, state_hash TEXT NOT NULL,
                revision INTEGER NOT NULL, head TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL, event_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL, kind TEXT NOT NULL, payload_json TEXT NOT NULL,
                actor TEXT NOT NULL, timestamp TEXT NOT NULL, before_hash TEXT NOT NULL, after_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS receipts (
                actor TEXT NOT NULL, command_id TEXT NOT NULL, request_hash TEXT NOT NULL,
                request_json TEXT NOT NULL, receipt_json TEXT NOT NULL, revision INTEGER UNIQUE NOT NULL,
                PRIMARY KEY(actor,command_id), FOREIGN KEY(revision) REFERENCES events(sequence));
            CREATE TABLE IF NOT EXISTS blobs (
                digest TEXT PRIMARY KEY, data BLOB NOT NULL, size INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY, revision INTEGER UNIQUE NOT NULL, head TEXT NOT NULL,
                state_json TEXT NOT NULL, state_hash TEXT NOT NULL, previous_id TEXT,
                FOREIGN KEY(revision) REFERENCES events(sequence));
            CREATE TABLE IF NOT EXISTS refusals (
                refusal_id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, actor TEXT NOT NULL,
                command_id TEXT, kind TEXT, request_hash TEXT, code TEXT NOT NULL, message TEXT NOT NULL,
                details_json TEXT);
        """
        # executescript implicitly commits pending transactions. Execute this
        # fixed SQL statement by statement so initialization and genesis are
        # one atomic transaction, including on invalid configuration or crash.
        for statement in schema.split(";"):
            if statement.strip():
                self._conn.execute(statement)

    @contextmanager
    def _transaction(self, immediate=True):
        self._conn.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
        try:
            yield
        except BaseException:
            self._conn.execute("ROLLBACK")
            raise
        else:
            self._conn.execute("COMMIT")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        with self._lock:
            if not self._closed:
                self._conn.close()
                self._closed = True

    def _current(self):
        row = self._conn.execute("SELECT * FROM materialized WHERE singleton=1").fetchone()
        if row is None:
            _fail("INTEGRITY_ERROR", "Materialized state is missing", 409)
        return json.loads(row["state_json"]), row["revision"], row["head"]

    def state(self):
        with self._lock:
            state, revision, head = self._current()
            return dict(state, revision=revision, head=head)

    @staticmethod
    def _event(row):
        return {"sequence": row["sequence"], "event_id": row["event_id"], "event_hash": row["event_hash"],
                "previous_hash": row["previous_hash"], "kind": row["kind"], "payload": json.loads(row["payload_json"]),
                "actor": row["actor"], "timestamp": row["timestamp"], "before_hash": row["before_hash"], "after_hash": row["after_hash"]}

    def events(self, after=0, limit=100):
        if type(after) is not int or after < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            _fail("INVALID_QUERY", "after must be a nonnegative integer and limit must be between 1 and 1000")
        with self._lock:
            return [self._event(row) for row in self._conn.execute(
                "SELECT * FROM events WHERE sequence > ? ORDER BY sequence LIMIT ?", (after, limit))]

    def get_command(self, command_id, actor=None):
        with self._lock:
            if actor is None:
                rows = self._conn.execute("SELECT receipt_json FROM receipts WHERE command_id=?", (command_id,)).fetchall()
                if len(rows) > 1:
                    _fail("AMBIGUOUS_COMMAND", "This command ID exists under several actors; specify the actor", 409)
                row = rows[0] if rows else None
            else:
                row = self._conn.execute("SELECT receipt_json FROM receipts WHERE command_id=? AND actor=?", (command_id, actor)).fetchone()
            if row is None:
                _fail("NOT_FOUND", "No applied command receipt has this ID", 404)
            return json.loads(row["receipt_json"])

    def get_checkpoint(self, checkpoint_id):
        with self._lock:
            row = self._conn.execute("SELECT * FROM checkpoints WHERE checkpoint_id=?", (checkpoint_id,)).fetchone()
            if row is None:
                _fail("NOT_FOUND", "Checkpoint does not exist", 404)
            return {"id": row["checkpoint_id"], "revision": row["revision"], "head": row["head"],
                    "state": json.loads(row["state_json"]), "state_hash": row["state_hash"], "previous_id": row["previous_id"]}

    def get_blob(self, digest):
        """Resolve captured bytes without consulting or executing live sources."""
        if not isinstance(digest, str) or not _HEX_DIGEST.fullmatch(digest):
            _fail("INVALID_QUERY", "Blob identity must be a lowercase SHA-256 digest")
        with self._lock:
            row = self._conn.execute("SELECT data,size FROM blobs WHERE digest=?", (digest,)).fetchone()
            if row is None:
                _fail("NOT_FOUND", "Captured byte object does not exist", 404)
            if type(row["size"]) is not int or len(row["data"]) != row["size"] or hashlib.sha256(row["data"]).hexdigest() != digest:
                _fail("INTEGRITY_ERROR", "Captured byte object is corrupt", 409)
            return bytes(row["data"])

    def refusals(self, limit=100):
        if type(limit) is not int or not 1 <= limit <= 1000:
            _fail("INVALID_QUERY", "limit must be between 1 and 1000")
        with self._lock:
            rows = self._conn.execute("SELECT * FROM refusals ORDER BY refusal_id DESC LIMIT ?", (limit,)).fetchall()
            result = []
            for row in reversed(rows):
                item = dict(row)
                item["details"] = json.loads(item.pop("details_json")) if row["details_json"] else None
                result.append(item)
            return result

    def _record_refusal(self, request, actor, error):
        try:
            request_hash = _hash(request)
        except (TypeError, ValueError, RecursionError):
            request_hash = None
        command_id = request.get("command_id") if isinstance(request, dict) else None
        kind = request.get("kind") if isinstance(request, dict) else None
        with self._transaction():
            self._conn.execute("INSERT INTO refusals(timestamp,actor,command_id,kind,request_hash,code,message,details_json) VALUES(?,?,?,?,?,?,?,?)",
                (_now(), str(actor)[:128], command_id if isinstance(command_id, str) else None,
                 kind if isinstance(kind, str) else None, request_hash, error.code, error.message,
                 _json(error.details) if error.details is not None else None))

    @staticmethod
    def _validate_request(request, actor, scopes):
        if "command" not in scopes:
            _fail("FORBIDDEN", "The actor does not have command scope", 403)
        if not isinstance(actor, str) or not actor.strip() or len(actor) > 128:
            _fail("INVALID_ACTOR", "Actor must be a stable nonempty name of at most 128 characters")
        if not isinstance(request, dict) or set(request) != {"command_id", "expected_revision", "kind", "payload"}:
            _fail("INVALID_REQUEST", "A command must contain exactly command_id, expected_revision, kind, and payload")
        if not isinstance(request["command_id"], str) or not _IDENTIFIER.fullmatch(request["command_id"]):
            _fail("INVALID_REQUEST", "command_id must be a stable ASCII identifier of at most 128 characters")
        if type(request["expected_revision"]) is not int or request["expected_revision"] < 0:
            _fail("INVALID_REQUEST", "expected_revision must be a nonnegative integer")
        if not isinstance(request["kind"], str) or request["kind"] not in COMMANDS:
            _fail("UNSUPPORTED_COMMAND", "The command kind is not registered")
        if not isinstance(request["payload"], dict):
            _fail("INVALID_REQUEST", "payload must be a JSON object")
        try:
            encoded = _json(request).encode("utf-8")
        except (TypeError, ValueError, RecursionError):
            _fail("INVALID_REQUEST", "Command must be finite JSON data")
        if len(encoded) > MAX_REQUEST_BYTES:
            _fail("REQUEST_TOO_LARGE", "Command exceeds the 64 KiB input budget", 413)

    def command(self, request, actor="operator", scopes=("command",)):
        with self._lock:
            try:
                self._validate_request(request, actor, scopes)
                request = json.loads(_json(request))  # Isolate caller-owned mutable structures.
                with self._transaction():
                    report = self._verify_locked()
                    if not report["ok"]:
                        _fail("INTEGRITY_ERROR", "Ledger integrity failed; command was not applied", 409, report)
                    request_hash = _hash(request)
                    prior = self._conn.execute("SELECT * FROM receipts WHERE actor=? AND command_id=?", (actor, request["command_id"])).fetchone()
                    if prior is not None:
                        if prior["request_hash"] != request_hash:
                            _fail("IDEMPOTENCY_CONFLICT", "This actor already used command_id for different command content", 409)
                        return json.loads(prior["receipt_json"])
                    state, revision, head = self._current()
                    if request["expected_revision"] != revision:
                        _fail("REVISION_CONFLICT", "The expected revision is stale", 409,
                              {"expected_revision": request["expected_revision"], "current_revision": revision})
                    sequence, timestamp = revision + 1, _now()
                    result = self._execute(request, state, sequence, actor, timestamp)
                    event = {"sequence": sequence, "event_id": str(uuid.uuid4()), "previous_hash": head,
                             "kind": request["kind"], "payload": {"request": request, "result": result},
                             "actor": actor, "timestamp": timestamp, "before_hash": _hash(state)}
                    updated = _reduce(state, event)
                    event["after_hash"] = _hash(updated)
                    event["event_hash"] = _hash(event)
                    self._conn.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?)", (
                        sequence, event["event_id"], event["event_hash"], head, event["kind"], _json(event["payload"]),
                        actor, timestamp, event["before_hash"], event["after_hash"]))
                    self._conn.execute("UPDATE materialized SET state_json=?,state_hash=?,revision=?,head=? WHERE singleton=1",
                                       (_json(updated), event["after_hash"], sequence, event["event_hash"]))
                    if request["kind"] == "checkpoint.create":
                        self._conn.execute("INSERT INTO checkpoints VALUES(?,?,?,?,?,?)", (
                            result["checkpoint_id"], sequence, event["event_hash"], _json(updated), event["after_hash"], result["previous_id"]))
                    receipt = {"ok": True, "command_id": request["command_id"], "actor": actor,
                               "revision": sequence, "head": event["event_hash"], "result": result}
                    self._conn.execute("INSERT INTO receipts VALUES(?,?,?,?,?,?)",
                        (actor, request["command_id"], request_hash, _json(request), _json(receipt), sequence))
                    return receipt
            except CommandError as error:
                self._record_refusal(request, actor, error)
                raise

    @staticmethod
    def _requirement(state, identifier):
        if not isinstance(identifier, str) or identifier not in state["requirements"]:
            _fail("UNKNOWN_REQUIREMENT", "Requirement is not in the captured constitution", 404)
        return state["requirements"][identifier]

    @staticmethod
    def _guidance(state, identifier):
        if not isinstance(identifier, str) or identifier not in state["guidance"]:
            _fail("UNKNOWN_GUIDANCE", "Guidance ID does not exist", 404)
        return state["guidance"][identifier]

    def _action(self, action, target, state):
        if action is None:
            return
        if not isinstance(action, dict):
            _fail("INVALID_PAYLOAD", "action must be a registered action object")
        kind = action.get("kind")
        if not isinstance(kind, str):
            _fail("UNSUPPORTED_ACTION", "Guidance action kind must be a registered name")
        if kind == "set_priority":
            _keys(action, ("kind", "target", "priority"))
            self._requirement(state, action["target"])
            if action["target"] != target:
                _fail("INVALID_PAYLOAD", "The action must affect the guidance target")
            if type(action["priority"]) is not int or not 0 <= action["priority"] <= 9:
                _fail("INVALID_PAYLOAD", "priority must be an integer from 0 to 9")
        elif kind in {"pause_research", "resume_research"}:
            _keys(action, ("kind",))
            if target != "research":
                _fail("INVALID_PAYLOAD", "Research actions require the research guidance target")
        else:
            _fail("UNSUPPORTED_ACTION", "Guidance action is not registered")

    def _execute(self, request, state, sequence, actor, timestamp):
        kind, payload = request["kind"], request["payload"]
        if kind == "guidance.submit":
            _keys(payload, ("target", "text"), ("action",))
            _text(payload["text"], "text", maximum=16000)
            if payload["target"] != "research":
                self._requirement(state, payload["target"])
            self._action(payload.get("action"), payload["target"], state)
            # Command IDs are actor scoped; guidance's public ID is still the
            # submitted command ID, so refuse cross-actor object collisions.
            if request["command_id"] in state["guidance"]:
                _fail("GUIDANCE_ID_CONFLICT", "This guidance ID already identifies another submission", 409)
            return {"guidance_id": request["command_id"], "status": "SUBMITTED"}
        if kind == "guidance.ack":
            _keys(payload, ("guidance_id", "disposition", "reason"))
            guidance = self._guidance(state, payload["guidance_id"])
            _text(payload["reason"], "reason")
            if not isinstance(payload["disposition"], str) or payload["disposition"] not in {"ACKNOWLEDGED", "DEFERRED", "REJECTED"}:
                _fail("INVALID_PAYLOAD", "Unknown acknowledgment disposition")
            if guidance["status"] in {"APPLIED", "REJECTED"}:
                _fail("INVALID_TRANSITION", "Applied or rejected guidance is closed", 409)
            return {"guidance_id": payload["guidance_id"], "status": payload["disposition"]}
        if kind == "guidance.apply":
            _keys(payload, ("guidance_id",))
            guidance = self._guidance(state, payload["guidance_id"])
            if guidance["status"] != "ACKNOWLEDGED":
                _fail("INVALID_TRANSITION", "Only acknowledged guidance may be applied", 409)
            action = guidance["action"]
            if action is None:
                _fail("NO_APPLICABLE_ACTION", "Text-only guidance has no executable registered action", 409)
            self._action(action, guidance["target"], state)
            if action["kind"] == "set_priority":
                effects = [{"path": f"requirements.{action['target']}.priority", "before": state["requirements"][action["target"]]["priority"], "after": action["priority"]}]
            else:
                effects = [{"path": "research.paused", "before": state["research"]["paused"], "after": action["kind"] == "pause_research"}]
            return {"guidance_id": payload["guidance_id"], "status": "APPLIED", "applied_revision": sequence, "effects": effects}
        if kind == "requirement.produce":
            _keys(payload, ("requirement_id", "artifacts"), ("note",))
            self._requirement(state, payload["requirement_id"])
            _text(payload.get("note", ""), "note", empty=True)
            artifacts = self._capture(payload["artifacts"])
            return {"requirement_id": payload["requirement_id"], "status": "PRODUCED", "artifacts": artifacts}
        if kind == "requirement.verify":
            _keys(payload, ("requirement_id",))
            requirement = self._requirement(state, payload["requirement_id"])
            if not requirement["artifacts"]:
                _fail("INVALID_TRANSITION", "Produce actual artifacts before verification", 409)
            verification = self._run_verifier(requirement, sequence, state)
            return {"requirement_id": payload["requirement_id"], "verification": verification,
                    "status": "VERIFIED" if verification["outcome"] == "PASS" else "PRODUCED"}
        if kind == "requirement.accept":
            _keys(payload, ("requirement_id",))
            requirement = self._requirement(state, payload["requirement_id"])
            verification = requirement["verification"]
            if requirement["status"] != "VERIFIED" or not verification or verification["outcome"] != "PASS":
                _fail("INVALID_TRANSITION", "Acceptance requires current passing verification", 409)
            self._check_artifacts(requirement["artifacts"])
            if not _same_json(verification.get("captured_artifacts"), requirement["artifacts"]):
                _fail("STALE_VERIFICATION", "Verified artifact identities do not match current captured artifacts", 409)
            if requirement["verifier"] == "scientific-contracts" and not _same_json(
                    verification["code_identity"], _code_identity("polyia.experiments")):
                _fail("STALE_VERIFICATION", "Scientific verification belongs to a different running implementation", 409)
            if requirement["verifier"] == "commission-evidence":
                from . import mission_verifiers
                binding, _ = mission_verifiers.prepare(self, requirement, state)
                if not _same_json(verification.get("mission_binding"), binding):
                    _fail("STALE_VERIFICATION", "Mission verification belongs to a different candidate, implementation or contract", 409)
            return {"requirement_id": payload["requirement_id"], "status": "ACCEPTED", "verification_revision": verification["revision"]}
        if kind == "checkpoint.create":
            _keys(payload, (), ("note",))
            _text(payload.get("note", ""), "note", empty=True)
            latest = state["latest_checkpoint"]
            context = self._capture_source_context(state["source_context"]["version"] + 1, sequence, timestamp)
            return {"checkpoint_id": f"cp-{sequence:08d}", "previous_id": latest["id"] if latest else None,
                    "source_context": context}
        if kind == "experiment.run":
            _keys(payload, ("name", "parameters"))
            if state["research"]["paused"]:
                _fail("RESEARCH_PAUSED", "Research is paused by applied guidance", 409)
            if not isinstance(payload["name"], str) or payload["name"] not in REGISTERED_EXPERIMENTS:
                _fail("UNSUPPORTED_EXPERIMENT", "Experiment name is not registered")
            self._validate_parameters(payload["parameters"], experiment=payload["name"])
            if payload["name"] in _EXTENSION_DEPENDENCIES_V1:
                return {"run": self._run_extension(request, sequence, actor, timestamp)}
            identity = _code_identity("polyia.store")
            try:
                from .experiments import run_registered
                identity = _code_identity("polyia.experiments")
                report = run_registered(payload["name"], payload["parameters"])
                self._validate_report(report)
                if not _same_json(identity, _code_identity("polyia.experiments")):
                    _fail("IMPLEMENTATION_CHANGED", "Scientific implementation changed during execution", 409)
            except Exception as error:
                # Faults at this trusted registered-code boundary are evidence,
                # not passing results. Signals/process death still abort the
                # transaction and are recovered by SQLite.
                report = {"status": "ERROR", "evidence_class": "NONE",
                          "result": {"error_type": type(error).__name__, "reason": str(error)[:1000]},
                          "checks": [], "limitations": ["The registered execution failed; no successful scientific result was obtained."]}
            run = {"id": request["command_id"], "name": payload["name"], "parameters": payload["parameters"],
                   "revision": sequence, "actor": actor, "timestamp": timestamp,
                   "code_identity": identity,
                   "versions": {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "polyia": __version__},
                   "report": report}
            return {"run": run}
        raise AssertionError("Request validation admitted an unregistered command")

    def _run_extension(self, request, sequence, actor, timestamp):
        name, parameters = request["payload"]["name"], request["payload"]["parameters"]
        identity = _code_identity("polyia.store")
        bundle = {"schema_version":1,"status":"NOT_EXECUTED",
                  "entrypoint":"polyia.capabilities.run_registered","modules":[]}
        try:
            pins = [_pinned_module(module_name) for module_name in _EXTENSION_DEPENDENCIES_V1[name]]
            captured = []
            for module, module_identity, source in pins:
                artifact = {"path":module_identity["module"].replace(".","/")+".py",
                            "sha256":module_identity["sha256"],"size":len(source)}
                self._conn.execute("INSERT OR IGNORE INTO blobs(digest,data,size) VALUES(?,?,?)",
                                   (artifact["sha256"],source,len(source)))
                captured.append({"identity":module_identity,"source":artifact})
            bundle.update(status="PINNED",modules=captured)
            identity = pins[0][1]
            report = pins[0][0].run_registered(name,parameters)
            self._validate_report(report)
            after = [_pinned_module(module_name)[1] for module_name in _EXTENSION_DEPENDENCIES_V1[name]]
            if not _same_json(after,[pin[1] for pin in pins]):
                _fail("IMPLEMENTATION_CHANGED","Extension source changed during execution",409)
        except sqlite3.DatabaseError:
            # Source custody and the event commit are one transaction. A storage
            # failure must roll it back, never leave unreferenced partial blobs.
            raise
        except Exception as error:
            report = {"status":"ERROR","evidence_class":"NONE",
                      "result":{"error_type":type(error).__name__,
                                "reason":error.code if isinstance(error,CommandError) else "EXECUTION_ERROR"},
                      "checks":[],"limitations":["The registered extension did not establish a successful result."]}
        bundle["digest"] = _hash(bundle)
        return {"id":request["command_id"],"name":name,"parameters":parameters,
                "revision":sequence,"actor":actor,"timestamp":timestamp,"code_identity":identity,
                "execution_bundle":bundle,
                "versions":{"python":platform.python_version(),"sqlite":sqlite3.sqlite_version,"polyia":__version__},
                "report":report}

    def _verify_execution_bundle(self, run, referenced_blobs):
        """Verify captured execution closure without importing/executing live code."""
        if run["name"] not in _EXTENSION_DEPENDENCIES_V1:
            if "execution_bundle" in run:
                raise ValueError("Legacy run carries an unregistered execution bundle")
            return
        bundle = run.get("execution_bundle")
        if (not isinstance(bundle,dict) or set(bundle) != {"schema_version","status","entrypoint","modules","digest"}
                or not _same_json(bundle["schema_version"],1)
                or bundle["entrypoint"] != "polyia.capabilities.run_registered"
                or bundle["digest"] != _hash({k:v for k,v in bundle.items() if k != "digest"})):
            raise ValueError("Extension execution bundle identity is malformed")
        if bundle["status"] == "NOT_EXECUTED":
            if bundle["modules"] != [] or run["report"]["status"] != "ERROR":
                raise ValueError("Unexecuted extension cannot certify a result or source closure")
            return
        if bundle["status"] != "PINNED" or type(bundle["modules"]) is not list:
            raise ValueError("Extension execution source status is invalid")
        expected = _EXTENSION_DEPENDENCIES_V1[run["name"]]
        if len(bundle["modules"]) != len(expected):
            raise ValueError("Extension execution dependency census differs")
        for module_name,item in zip(expected,bundle["modules"]):
            if not isinstance(item,dict) or set(item) != {"identity","source"}:
                raise ValueError("Malformed extension dependency entry")
            identity, artifact = item["identity"],item["source"]
            if (not isinstance(identity,dict) or set(identity) != {"module","sha256","loaded_code_sha256","package_version","python_version","source_binding"}
                    or identity["module"] != module_name or identity["source_binding"] != "PINNED_SOURCE_MATCHES_LOADED_CODE"
                    or not isinstance(identity["loaded_code_sha256"],str) or not _HEX_DIGEST.fullmatch(identity["loaded_code_sha256"])
                    or not isinstance(identity["sha256"],str) or not _HEX_DIGEST.fullmatch(identity["sha256"])
                    or not isinstance(artifact,dict) or set(artifact) != {"path","sha256","size"}
                    or artifact["path"] != module_name.replace(".","/")+".py" or artifact["sha256"] != identity["sha256"]
                    or type(artifact["size"]) is not int or not 0 < artifact["size"] <= MAX_CONTEXT_FILE_BYTES):
                raise ValueError("Extension source does not bind its recorded loaded identity")
            self._check_artifacts([artifact])
            referenced_blobs.add(artifact["sha256"])
        if not _same_json(run["code_identity"],bundle["modules"][0]["identity"]):
            raise ValueError("Extension entrypoint identity differs from its captured source")
        self._validate_report(run["report"])

    @staticmethod
    def _validate_parameters(parameters, *, experiment=None):
        if not isinstance(parameters, dict):
            _fail("INVALID_PAYLOAD", "parameters must be a JSON object")
        # Loss records and retained codepoints make a valid mark-rich recovery
        # larger than the generic value census. Only this exact, versioned
        # recovery envelope receives the bounded allowance; the 64 KiB command,
        # depth, string and integer limits still apply before execution.
        rasm_recovery = (experiment == "rasm" and parameters.get("operation") == "recover"
                         and parameters.get("version") == "polyia.rasm/0.1"
                         and parameters.get("chart") == "timeless.rsa28/0.1"
                         and set(parameters) == {"version", "chart", "operation", "projection", "side_data"})
        # A returned serialized word can exceed the generic scalar-string cap.
        # Only this exact versioned deserialize envelope receives a text grant;
        # node/depth and complete 64 KiB command limits remain unchanged.
        forms_deserialization = (experiment == "forms" and parameters.get("version") == "polyia.forms/0.1"
                                 and parameters.get("operation") == "deserialize"
                                 and {"version", "operation", "alphabet", "text"} <= set(parameters)
                                 <= {"version", "operation", "alphabet", "text", "budgets"})
        item_budget = 8192 if rasm_recovery else 2048
        count = 0
        stack = [(parameters, 0, ())]
        while stack:
            value, depth, path = stack.pop()
            count += 1
            if depth > 12 or count > item_budget:
                _fail("RESOURCE_LIMIT", "Experiment parameters exceed the depth or item budget")
            if isinstance(value, dict):
                stack.extend((v, depth + 1, path + (key,)) for key,v in value.items())
            elif isinstance(value, list):
                stack.extend((v, depth + 1, path + (index,)) for index,v in enumerate(value))
            elif isinstance(value, str):
                long_source = (experiment == "native" and path == ("source",)) or (experiment == "intake" and path == ("text",))
                serialized_word = forms_deserialization and path == ("text",)
                if long_source or serialized_word:
                    try:
                        size = len(value.encode("utf-8"))
                    except UnicodeError:
                        _fail("INVALID_PAYLOAD", "Source/text must contain valid Unicode scalar values")
                    if serialized_word and size > 48 * 1024:
                        _fail("RESOURCE_LIMIT", "Forms serialized text exceeds 48 KiB UTF-8 bytes")
                    if long_source and size > 16384:
                        _fail("RESOURCE_LIMIT", "Native/intake source exceeds 16384 UTF-8 bytes")
                elif len(value) > 2048:
                    _fail("RESOURCE_LIMIT", "Experiment parameter strings exceed 2048 characters")
            elif type(value) is int and value.bit_length() > 4096:
                _fail("RESOURCE_LIMIT", "Experiment integers exceed the bit budget")

    @staticmethod
    def _validate_report(report):
        if not isinstance(report, dict) or not {"status", "evidence_class", "result", "checks", "limitations"} <= set(report):
            raise ValueError("Registered experiment returned an invalid report")
        if not isinstance(report["checks"], list) or not isinstance(report["limitations"], list):
            raise ValueError("Report checks and limitations must be lists")
        if report["status"] not in {"PASS", "FAIL", "REFUSED", "ERROR", "INCONCLUSIVE", "RESOURCE_LIMIT"}:
            raise ValueError("Report status is not an admitted evidence outcome")
        if not isinstance(report["evidence_class"], str) or not report["evidence_class"].strip():
            raise ValueError("Report must name its evidence class")
        if any(not isinstance(check, dict) or not isinstance(check.get("name"), str)
               or type(check.get("pass")) is not bool for check in report["checks"]):
            raise ValueError("Every check needs a name and an explicit boolean pass result")
        if report["status"] == "PASS" and (not report["checks"] or not all(check["pass"] for check in report["checks"])):
            raise ValueError("PASS cannot be inferred from empty or failing checks")
        if len(_json(report).encode("utf-8")) > MAX_RESULT_BYTES:
            raise ValueError("Experiment report exceeds the result budget")

    def _science_inputs(self, artifacts, state, identity):
        inputs, ancillary, linked_runs = [], [], []
        kernels = [artifact for artifact in artifacts if artifact["sha256"] == identity["sha256"]]
        if not kernels:
            _fail("PRODUCED_KERNEL_MISMATCH", "Produce the exact pinned experiments.py bytes before scientific verification", 409)
        for artifact in artifacts:
            if artifact["sha256"] == identity["sha256"]:
                inputs.append(dict(artifact, role="executing-kernel", module="polyia.experiments"))
                continue
            document = None
            if artifact["path"].lower().endswith(".json"):
                try:
                    document = json.loads(self.get_blob(artifact["sha256"]))
                except (ValueError, UnicodeError, RecursionError):
                    document = None
            is_receipt = isinstance(document, dict) and isinstance(document.get("result"), dict) and "run" in document["result"]
            is_run = isinstance(document, dict) and "report" in document
            is_report = isinstance(document, dict) and "status" in document and ("checks" in document or "evidence_class" in document)
            if not (is_receipt or is_run or is_report):
                ancillary.append(dict(artifact, role="ancillary"))
                continue
            candidate = document
            if is_receipt:
                try:
                    recorded = self.get_command(document.get("command_id"), actor=document.get("actor"))
                except (CommandError, TypeError, sqlite3.Error):
                    recorded = None
                if recorded is None or not _same_json(document, recorded):
                    _fail("UNLINKED_RUN_RECEIPT", "The attached receipt does not exactly match a committed command", 409, {"path": artifact["path"]})
                candidate = document["result"]["run"]
            linked = next((run for run in state["runs"] if _same_json(run, candidate)), None)
            if (linked is None or linked["name"] != "acceptance" or not _same_json(linked["parameters"], {})
                    or linked["report"]["status"] != "PASS" or not _same_json(linked["code_identity"], identity)):
                _fail("UNLINKED_RUN_RECEIPT", "An attached scientific report must exactly match a passing committed acceptance run of this implementation", 409,
                      {"path": artifact["path"]})
            linked_runs.append(linked)
            inputs.append(dict(artifact, role="recorded-run", run_id=linked["id"], run_revision=linked["revision"]))
        return inputs, ancillary, linked_runs

    def _run_verifier(self, requirement, sequence, state):
        self._check_artifacts(requirement["artifacts"])
        name = requirement["verifier"]
        result = {"verifier": name, "captured_artifacts": deepcopy(requirement["artifacts"]),
                  "inputs": [], "ancillary_attachments": [], "revision": sequence,
                  "code_identity": _code_identity("polyia.store")}
        if name == "artifact-integrity":
            result["inputs"] = deepcopy(requirement["artifacts"])
            result.update(outcome="PASS", evidence_class="ARTIFACT_INTEGRITY", report={
                "checked_artifacts": len(requirement["artifacts"]),
                "limitations": ["Captured bytes are intact; their scientific truth and sufficiency are not established."]})
        elif name == "scientific-contracts":
            try:
                from .experiments import run_registered
                result["code_identity"] = _code_identity("polyia.experiments")
                inputs, ancillary, linked_runs = self._science_inputs(requirement["artifacts"], state, result["code_identity"])
                result["inputs"], result["ancillary_attachments"] = inputs, ancillary
                report = run_registered("acceptance", {})
                self._validate_report(report)
                if not _same_json(result["code_identity"], _code_identity("polyia.experiments")):
                    _fail("IMPLEMENTATION_CHANGED", "Scientific implementation changed during verification", 409)
                if any(not _same_json(run["report"], report) for run in linked_runs):
                    _fail("REPRODUCTION_MISMATCH", "The fresh exact check differs from the attached committed run", 409)
                passed = report["status"] == "PASS" and bool(report["checks"]) and all(
                    isinstance(check, dict) and check.get("pass") is True for check in report["checks"])
                result.update(outcome="PASS" if passed else "FAIL", evidence_class=report["evidence_class"], report=report)
            except CommandError as error:
                result.update(outcome="ERROR" if error.code == "IMPLEMENTATION_CHANGED" else "FAIL", evidence_class="NONE",
                              report={"reason": error.code, "detail": error.message, "details": error.details})
            except Exception as error:
                result.update(outcome="ERROR", evidence_class="NONE", report={"reason": type(error).__name__, "detail": str(error)[:1000]})
        elif name == "commission-evidence" and requirement["id"] in {"PIA-042", "PIA-040"}:
            try:
                from . import mission_verifiers
                binding, contract = mission_verifiers.prepare(self, requirement, state)
                report = (mission_verifiers.run_guidance_checks() if requirement["id"] == "PIA-040"
                          else mission_verifiers.run_capture_checks())
                self._validate_report(report)
                after, repeated_contract = mission_verifiers.prepare(self, requirement, state)
                if not _same_json(binding, after) or contract != repeated_contract:
                    _fail("IMPLEMENTATION_CHANGED", "Mission implementation or contract changed during verification", 409)
                artifact = binding["contract"]
                self._conn.execute("INSERT OR IGNORE INTO blobs(digest,data,size) VALUES(?,?,?)",
                                   (artifact["sha256"], contract, len(contract)))
                result.update(mission_binding=binding, inputs=deepcopy(requirement["artifacts"]),
                              code_identity=deepcopy(binding["implementation"][-1]["identity"]),
                              outcome="PASS" if report["status"] == "PASS" else "FAIL",
                              evidence_class=report["evidence_class"], report=report)
            except CommandError as error:
                result.update(outcome="ERROR" if error.code == "IMPLEMENTATION_CHANGED" else "FAIL", evidence_class="NONE",
                              report={"reason": error.code, "detail": error.message})
            except Exception as error:
                result.update(outcome="ERROR", evidence_class="NONE",
                              report={"reason": type(error).__name__, "detail": str(error)[:1000]})
        else:
            result.update(outcome="UNSUPPORTED", evidence_class="NONE", report={"reason": "No registered verifier is available for this requirement"})
        return result

    def _verify_mission_receipt(self, requirement, verification, state, referenced_blobs):
        """Validate retained version-one bindings without importing/running the adapter."""
        binding = verification.get("mission_binding")
        if binding is None:
            return  # Historical unsupported attempts and failures before binding.
        adapters = {"PIA-042": "PIA-042/capture-v1", "PIA-040": "PIA-040/guidance-effects-v1"}
        if (not isinstance(binding, dict) or type(binding.get("schema_version")) is not int
                or binding["schema_version"] != 1 or binding.get("adapter") != adapters.get(requirement["id"])
                or requirement["id"] not in adapters or binding.get("requirement_id") != requirement["id"]
                or verification.get("verifier") != "commission-evidence"
                or binding.get("digest") != _hash({k: v for k, v in binding.items() if k != "digest"})
                or not _same_json(binding.get("captured_artifacts"), requirement["artifacts"])
                or not _same_json(binding.get("production_revision"), requirement.get("produced_revision"))
                or binding.get("production_actor") != requirement.get("produced_by")
                or binding.get("source_context_digest") != state["source_context"]["digest"]):
            raise ValueError("Mission verification binding does not match its production")
        contract_blob = binding["contract"]
        self._check_artifacts([contract_blob])
        referenced_blobs.add(contract_blob["sha256"])
        contract = json.loads(self.get_blob(contract_blob["sha256"]))
        genesis = json.loads(self._conn.execute("SELECT document_json FROM genesis WHERE singleton=1").fetchone()[0])
        definition = genesis["definitions"][requirement["id"]]
        if (contract.get("adapter") != binding["adapter"] or not _same_json(contract.get("schema_version"), 1)
                or not _same_json(contract.get("definition"), definition)
                or binding.get("definition_sha256") != _hash(definition)):
            raise ValueError("Mission contract differs from its immutable requirement")
        expected = {"polyia": "polyia/__init__.py", "polyia.store": "polyia/store.py",
                    "polyia.experiments": "polyia/experiments.py", "polyia.mission_verifiers": "polyia/mission_verifiers.py"}
        seen = set()
        for module in binding["implementation"]:
            identity, artifact = module["identity"], module["source"]
            name = identity["module"]
            if (name not in expected or name in seen or artifact["path"] != expected[name]
                    or artifact not in requirement["artifacts"] or identity["sha256"] != artifact["sha256"]
                    or not _HEX_DIGEST.fullmatch(identity["loaded_code_sha256"])
                    or identity["source_binding"] != "PINNED_SOURCE_MATCHES_LOADED_CODE"):
                raise ValueError("Mission implementation identity is inconsistent")
            self._check_artifacts([artifact])
            referenced_blobs.add(artifact["sha256"])
            seen.add(name)
        if seen != set(expected):
            raise ValueError("Mission implementation dependency is missing")
        self._validate_report(verification["report"])
        if (verification["outcome"] == "PASS") != (verification["report"]["status"] == "PASS"):
            raise ValueError("Mission outcome differs from its retained report")

    @staticmethod
    def _safe_artifact_name(path):
        if not isinstance(path, str) or not path or len(path) > 1024 or "\\" in path or "\x00" in path:
            _fail("UNSAFE_ARTIFACT", "Artifact path must be a safe relative POSIX path")
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or any(part in {"", ".", ".."} for part in path.split("/")):
            _fail("UNSAFE_ARTIFACT", "Artifact path must stay inside the workspace")
        for part in candidate.parts:
            name = part.lower()
            if (name.startswith(".") or name in {"secrets", "credentials", "id_rsa", "id_ed25519", "private_key"}
                    or any(word in name for word in ("secret", "credential", "password", "token", "api_key", "apikey", "private-key"))
                    or name.endswith((".key", ".pem", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db", "-wal", "-shm"))):
                _fail("UNSAFE_ARTIFACT", "Runtime data, hidden files, and secret-like filenames cannot be captured")
        return candidate

    def _capture_one(self, path, *, root=None, maximum=MAX_ARTIFACT_BYTES):
        if not getattr(os, "O_NOFOLLOW", 0) or not getattr(os, "O_DIRECTORY", 0) or os.open not in os.supports_dir_fd:
            _fail("UNSUPPORTED_PLATFORM", "Safe artifact capture requires POSIX directory descriptors and O_NOFOLLOW", 501)
        relative = self._safe_artifact_name(path)
        root = self.workspace if root is None else root
        full = root.joinpath(*relative.parts)
        try:
            resolved = full.resolve(strict=True)
        except (FileNotFoundError, RuntimeError, OSError):
            _fail("MISSING_ARTIFACT", "Artifact is unavailable", details={"path": path})
        if not resolved.is_relative_to(root):
            _fail("UNSAFE_ARTIFACT", "Artifact escapes the workspace", details={"path": path})
        if resolved == self.db_path or resolved.is_relative_to(self.db_path.parent):
            # A state directory equal to the entire workspace is discouraged;
            # still deny only the database and its sidecars in that case.
            if self.db_path.parent != self.workspace or resolved.name.startswith(self.db_path.name):
                _fail("UNSAFE_ARTIFACT", "Runtime data cannot be captured as evidence", details={"path": path})
        # Walk from a directory descriptor and refuse every symlink. This avoids
        # the resolve/open race that could otherwise expose an external file.
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        descriptor = None
        try:
            for component in relative.parts[:-1]:
                next_directory = os.open(component, flags | os.O_DIRECTORY, dir_fd=directory)
                os.close(directory)
                directory = next_directory
            descriptor = os.open(relative.name, flags | getattr(os, "O_NONBLOCK", 0), dir_fd=directory)
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode):
                _fail("UNSAFE_ARTIFACT", "Only regular files may be captured", details={"path": path})
            if before.st_size > maximum:
                _fail("RESOURCE_LIMIT", "A file exceeds its declared capture byte limit", details={"path": path, "maximum_bytes": maximum})
            chunks, count = [], 0
            while True:
                chunk = os.read(descriptor, min(1024 * 1024, maximum + 1 - count))
                if not chunk:
                    break
                chunks.append(chunk)
                count += len(chunk)
                if count > maximum:
                    _fail("RESOURCE_LIMIT", "An artifact grew beyond the capture limit")
            after = os.fstat(descriptor)
            if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                _fail("ARTIFACT_CHANGED", "Artifact changed during capture; retry with a stable file", 409)
            data = b"".join(chunks)
            if not data:
                _fail("EMPTY_ARTIFACT", "Empty files are not accepted as produced evidence", details={"path": path})
            return data
        except OSError:
            _fail("UNSAFE_ARTIFACT", "Artifact could not be safely opened without following symlinks", details={"path": path})
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(directory)

    def _capture(self, paths):
        if not isinstance(paths, list) or not 1 <= len(paths) <= 32 or any(not isinstance(path, str) for path in paths):
            _fail("INVALID_PAYLOAD", "artifacts must contain between 1 and 32 relative file paths")
        if len(set(paths)) != len(paths):
            _fail("INVALID_PAYLOAD", "Artifact paths must be unique")
        artifacts, total = [], 0
        for path in paths:
            data = self._capture_one(path)
            total += len(data)
            if total > MAX_CAPTURE_BYTES:
                _fail("RESOURCE_LIMIT", "Combined artifacts exceed the 32 MiB capture limit")
            digest = hashlib.sha256(data).hexdigest()
            self._conn.execute("INSERT OR IGNORE INTO blobs(digest,data,size) VALUES(?,?,?)", (digest, data, len(data)))
            artifacts.append({"path": path, "sha256": digest, "size": len(data)})
        return artifacts

    def _capture_source_context(self, version, revision, timestamp):
        """Capture bounded control documents, never the referenced corpus body."""
        registry_root = PACKAGE_ROOT if self._context_mode == "package" else self.workspace
        scientific_identity = _code_identity("polyia.experiments")
        objects, missing, total = [], [], 0
        constitution_hash = None
        manifest_hash = None
        for origin, root, entries in ((self._context_mode, registry_root, CONTEXT_REGISTRIES),
                                      ("package", PACKAGE_ROOT, CONTEXT_CODE)):
            for role, path, required in entries:
                metadata = {"role": role, "path": path, "origin": origin, "required": required}
                try:
                    data = self._capture_one(path, root=root, maximum=MAX_CONTEXT_FILE_BYTES)
                except CommandError as error:
                    if error.code not in {"MISSING_ARTIFACT", "UNSAFE_ARTIFACT", "EMPTY_ARTIFACT"}:
                        raise
                    missing.append(dict(metadata, status="UNAVAILABLE", reason=error.code))
                    continue
                total += len(data)
                if total > MAX_CONTEXT_BYTES:
                    _fail("RESOURCE_LIMIT", "Source context exceeds the 8 MiB aggregate capture budget")
                if path.endswith(".json"):
                    try:
                        document = json.loads(data)
                        if not isinstance(document, dict):
                            raise ValueError("Context registry must be an object")
                        _json(document)
                        if role == "constitution":
                            definitions = document.get("requirements")
                            if not isinstance(definitions, list):
                                raise ValueError("Captured constitution must contain a requirements list")
                            constitution_hash = _hash(_definitions(definitions))
                    except (ValueError, TypeError, RecursionError) as error:
                        _fail("INVALID_SOURCE_CONTEXT", "A controlling registry is not valid bounded JSON", 409,
                              {"path": path, "reason": str(error)[:300]})
                digest = hashlib.sha256(data).hexdigest()
                if path == "polyia/experiments.py" and digest != scientific_identity["sha256"]:
                    _fail("IMPLEMENTATION_CHANGED", "Scientific source changed while context was captured", 409)
                self._conn.execute("INSERT OR IGNORE INTO blobs(digest,data,size) VALUES(?,?,?)", (digest, data, len(data)))
                objects.append(dict(metadata, sha256=digest, size=len(data)))
                if role == "source-manifest":
                    manifest_hash = digest
        mandatory_registry_count = sum(item["role"] in {"constitution", "source-manifest", "authority"} for item in objects)
        status = "UNSOURCED" if mandatory_registry_count == 0 else "INCOMPLETE" if any(item["required"] for item in missing) else "SOURCED"
        binding = "UNAVAILABLE" if constitution_hash is None else "MATCH" if constitution_hash == self._genesis_definitions_hash else "DIFFERENT"
        context = {"schema_version": 1, "version": version, "captured_revision": revision, "captured_at": timestamp,
                   "registry_origin": self._context_mode, "status": status, "objects": objects, "missing": missing,
                   "definition_binding": {"status": binding, "genesis_definitions_sha256": self._genesis_definitions_hash,
                                          "captured_constitution_requirements_sha256": constitution_hash},
                   "external_sources": {"source_manifest_sha256": manifest_hash, "storage": "IMMUTABLE_PACKAGE_FILES",
                                        "corpus_bytes_copied": 0, "verification_scope": "Manifest bytes captured; corpus files remain external"},
                   "execution_context": {"runtime_version": __version__, "python_version": platform.python_version(),
                                         "sqlite_version": sqlite3.sqlite_version, "scientific_kernel": scientific_identity}}
        if not _same_json(scientific_identity, _code_identity("polyia.experiments")):
            _fail("IMPLEMENTATION_CHANGED", "Scientific source changed during context capture", 409)
        context["digest"] = _hash(context)
        return context

    def _verify_source_context(self, context, version, revision, definitions_hash, mode, referenced_blobs):
        if (not isinstance(context, dict) or not _same_json(context.get("schema_version"), 1)
                or not _same_json(context.get("version"), version) or not _same_json(context.get("captured_revision"), revision)
                or context.get("registry_origin") != mode or mode not in {"package", "workspace"}
                or context.get("digest") != _hash({key: value for key, value in context.items() if key != "digest"})):
            raise ValueError("Source context identity, version or source mode is inconsistent")
        expected = {(origin, role, path): required
                    for origin, entries in ((mode, CONTEXT_REGISTRIES), ("package", CONTEXT_CODE))
                    for role, path, required in entries}
        seen, constitution_hash, manifest_hash, total = set(), None, None, 0
        for item in context["objects"]:
            key = (item["origin"], item["role"], item["path"])
            if key not in expected or key in seen or not _same_json(item["required"], expected[key]):
                raise ValueError("Source context object identity is unregistered or duplicated")
            if type(item["size"]) is not int or not 0 < item["size"] <= MAX_CONTEXT_FILE_BYTES:
                raise ValueError("Source context object violates its byte budget")
            self._check_artifacts([item])
            data = self.get_blob(item["sha256"])
            total += len(data)
            if item["role"] == "constitution":
                constitution = json.loads(data)
                requirements = constitution.get("requirements")
                if not isinstance(requirements, list):
                    raise ValueError("Captured constitution has no requirement definitions")
                constitution_hash = _hash(_definitions(requirements))
            if item["role"] == "source-manifest":
                manifest_hash = item["sha256"]
            seen.add(key)
            referenced_blobs.add(item["sha256"])
        for item in context["missing"]:
            key = (item["origin"], item["role"], item["path"])
            if (key not in expected or key in seen or item["status"] != "UNAVAILABLE"
                    or not _same_json(item["required"], expected[key]) or not isinstance(item["reason"], str)):
                raise ValueError("Source context missing-item flags are inconsistent")
            seen.add(key)
        if seen != set(expected) or total > MAX_CONTEXT_BYTES:
            raise ValueError("Source context inventory is incomplete or exceeds its budget")
        available = sum(item["role"] in {"constitution", "source-manifest", "authority"} for item in context["objects"])
        status = "UNSOURCED" if available == 0 else "INCOMPLETE" if any(item["required"] for item in context["missing"]) else "SOURCED"
        binding = {"status": "UNAVAILABLE" if constitution_hash is None else "MATCH" if constitution_hash == definitions_hash else "DIFFERENT",
                   "genesis_definitions_sha256": definitions_hash, "captured_constitution_requirements_sha256": constitution_hash}
        if (context["status"] != status or not _same_json(context["definition_binding"], binding)
                or context["external_sources"]["source_manifest_sha256"] != manifest_hash
                or not _same_json(context["external_sources"]["corpus_bytes_copied"], 0)):
            raise ValueError("Source context authority/definition binding is inconsistent")
        scientific_sources = [item for item in context["objects"] if item["path"] == "polyia/experiments.py" and item["origin"] == "package"]
        identity = context["execution_context"]["scientific_kernel"]
        if (len(scientific_sources) != 1 or identity["sha256"] != scientific_sources[0]["sha256"]
                or identity["module"] != "polyia.experiments" or not _HEX_DIGEST.fullmatch(identity["loaded_code_sha256"])
                or identity["source_binding"] != "PINNED_SOURCE_MATCHES_LOADED_CODE"):
            raise ValueError("Source context does not bind its recorded executing scientific kernel")

    def _check_artifacts(self, artifacts):
        if not artifacts:
            _fail("INTEGRITY_ERROR", "An evidence snapshot contains no captured artifacts", 409)
        for artifact in artifacts:
            digest = artifact["sha256"]
            row = self._conn.execute("SELECT data,size FROM blobs WHERE digest=?", (digest,)).fetchone()
            if row is None or row["size"] != artifact["size"] or len(row["data"]) != row["size"] or hashlib.sha256(row["data"]).hexdigest() != digest:
                _fail("INTEGRITY_ERROR", "Captured artifact bytes do not match their recorded digest", 409,
                      {"path": artifact["path"], "sha256": digest})

    def checkpoint(self, note=""):
        """Local convenience; HTTP mutations must call command explicitly."""
        return self.command({"command_id": str(uuid.uuid4()), "expected_revision": self.state()["revision"],
                             "kind": "checkpoint.create", "payload": {"note": note}})

    def verify(self):
        with self._lock, self._transaction(immediate=False):
            report = self._verify_locked()
            report["workspace_drift"] = self._workspace_drift() if report["ok"] else {
                "evaluated": False, "reason": "Captured ledger integrity failed", "changed": None, "artifacts": []}
            return report

    def _workspace_drift(self):
        """Report live-source differences separately from immutable evidence."""
        state, _, _ = self._current()
        artifacts = []
        for requirement_id, requirement in state["requirements"].items():
            for artifact in requirement["artifacts"]:
                item = {"requirement_id": requirement_id, "path": artifact["path"], "captured_sha256": artifact["sha256"]}
                try:
                    data = self._capture_one(artifact["path"])
                    actual = hashlib.sha256(data).hexdigest()
                    item.update(status="UNCHANGED" if actual == artifact["sha256"] else "MODIFIED", live_sha256=actual)
                except CommandError as error:
                    status = "MISSING" if error.code == "MISSING_ARTIFACT" else "MODIFIED" if error.code == "EMPTY_ARTIFACT" else "UNAVAILABLE"
                    item.update(status=status, reason=error.code)
                artifacts.append(item)
        return {"evaluated": True, "changed": sum(item["status"] != "UNCHANGED" for item in artifacts),
                "artifacts": artifacts, "interpretation": "Live workspace drift does not alter acceptance of a captured historical snapshot"}

    def _verify_locked(self):
        checked = {"events": 0, "receipts": 0, "blobs": 0, "checkpoints": 0, "source_contexts": 0}
        diagnostics = []
        try:
            tables = {row[0] for row in self._conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not LEDGER_TABLES <= tables:
                raise ValueError("Required ledger tables are missing")
            quick = self._conn.execute("PRAGMA quick_check").fetchone()[0]
            if quick != "ok":
                raise ValueError("SQLite quick_check failed")
            row = self._conn.execute("SELECT * FROM genesis WHERE singleton=1").fetchone()
            if row is None:
                raise ValueError("Genesis record is missing")
            genesis = json.loads(row["document_json"])
            if _hash(genesis) != row["digest"] or not _same_json(genesis["schema_version"], SCHEMA_VERSION):
                raise ValueError("Genesis digest or schema differs")
            if not _same_json(genesis["state"], _initial_state(genesis["definitions"], genesis["source_context"])):
                raise ValueError("Genesis state does not match its requirement definitions")
            state, head, revision = genesis["state"], row["digest"], 0
            checkpoints, referenced_blobs = {}, set()
            context_version = 1
            definitions_hash = _hash(genesis["definitions"])
            self._verify_source_context(genesis["source_context"], context_version, 0, definitions_hash,
                                        genesis["context_mode"], referenced_blobs)
            checked["source_contexts"] += 1
            for row in self._conn.execute("SELECT * FROM events ORDER BY sequence"):
                event = self._event(row)
                sequence = event["sequence"]
                if sequence != revision + 1 or event["previous_hash"] != head:
                    raise ValueError(f"Broken event sequence or previous hash at {sequence}")
                contents = {key: value for key, value in event.items() if key != "event_hash"}
                if _hash(contents) != event["event_hash"]:
                    raise ValueError(f"Event hash mismatch at {sequence}")
                if event["before_hash"] != _hash(state):
                    raise ValueError(f"Before-state digest mismatch at {sequence}")
                request = event["payload"]["request"]
                self._validate_request(request, event["actor"], ("command",))
                if request["kind"] != event["kind"] or request["expected_revision"] != revision:
                    raise ValueError(f"Event/request mismatch at {sequence}")
                updated = _reduce(state, event)
                if _hash(updated) != event["after_hash"]:
                    raise ValueError(f"Replayed state digest mismatch at {sequence}")
                receipt_row = self._conn.execute("SELECT * FROM receipts WHERE revision=?", (sequence,)).fetchone()
                expected_receipt = {"ok": True, "command_id": request["command_id"], "actor": event["actor"],
                                    "revision": sequence, "head": event["event_hash"], "result": event["payload"]["result"]}
                if (receipt_row is None or receipt_row["actor"] != event["actor"] or receipt_row["command_id"] != request["command_id"]
                        or receipt_row["request_hash"] != _hash(request)
                        or _hash(json.loads(receipt_row["request_json"])) != receipt_row["request_hash"]
                        or not _same_json(json.loads(receipt_row["request_json"]), request)
                        or not _same_json(json.loads(receipt_row["receipt_json"]), expected_receipt)):
                    raise ValueError(f"Command receipt mismatch at {sequence}")
                checked["receipts"] += 1
                if event["kind"] == "requirement.produce":
                    artifacts = event["payload"]["result"]["artifacts"]
                    if not artifacts:
                        raise ValueError(f"Empty artifact capture at {sequence}")
                    for artifact in artifacts:
                        if not _HEX_DIGEST.fullmatch(artifact["sha256"]) or type(artifact["size"]) is not int or artifact["size"] <= 0:
                            raise ValueError(f"Malformed artifact identity at {sequence}")
                        self._check_artifacts([artifact])
                        referenced_blobs.add(artifact["sha256"])
                if event["kind"] == "requirement.verify":
                    requirement = state["requirements"][request["payload"]["requirement_id"]]
                    verification = event["payload"]["result"]["verification"]
                    self._verify_mission_receipt(requirement, verification, state, referenced_blobs)
                if event["kind"] == "experiment.run":
                    run = event["payload"]["result"]["run"]
                    if (run["name"] != request["payload"]["name"] or not _same_json(run["parameters"],request["payload"]["parameters"])
                            or run["id"] != request["command_id"] or not _same_json(run["revision"],sequence)
                            or run["actor"] != event["actor"] or run["timestamp"] != event["timestamp"]):
                        raise ValueError("Experiment run does not match its recorded request")
                    self._verify_execution_bundle(run,referenced_blobs)
                if event["kind"] == "checkpoint.create":
                    context_version += 1
                    self._verify_source_context(updated["source_context"], context_version, sequence, definitions_hash,
                                                genesis["context_mode"], referenced_blobs)
                    checked["source_contexts"] += 1
                    checkpoint = updated["latest_checkpoint"]
                    checkpoints[checkpoint["id"]] = {"revision": sequence, "head": event["event_hash"], "state": updated,
                                                      "state_hash": event["after_hash"], "previous_id": checkpoint["previous_id"]}
                state, head, revision = updated, event["event_hash"], sequence
                checked["events"] += 1
            if self._conn.execute("SELECT COUNT(*) FROM receipts").fetchone()[0] != revision:
                raise ValueError("Receipt count does not match the committed journal")
            current = self._conn.execute("SELECT * FROM materialized WHERE singleton=1").fetchone()
            if (current is None or current["revision"] != revision or current["head"] != head
                    or current["state_hash"] != _hash(state)
                    or current["state_hash"] != _hash(json.loads(current["state_json"]))
                    or not _same_json(json.loads(current["state_json"]), state)):
                raise ValueError("Current materialized state differs from deterministic replay")
            for row in self._conn.execute("SELECT * FROM blobs"):
                if (row["digest"] not in referenced_blobs or len(row["data"]) != row["size"]
                        or hashlib.sha256(row["data"]).hexdigest() != row["digest"]):
                    raise ValueError("Captured blob is corrupt or has no committed source event")
                checked["blobs"] += 1
            for row in self._conn.execute("SELECT * FROM checkpoints"):
                expected = checkpoints.pop(row["checkpoint_id"], None)
                actual = {"revision": row["revision"], "head": row["head"], "state": json.loads(row["state_json"]),
                          "state_hash": row["state_hash"], "previous_id": row["previous_id"]}
                if expected is None or row["state_hash"] != _hash(actual["state"]) or not _same_json(expected, actual):
                    raise ValueError("Stored checkpoint differs from its source event and replayed state")
                checked["checkpoints"] += 1
            if checkpoints:
                raise ValueError("A committed checkpoint snapshot is missing")
        except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError, sqlite3.DatabaseError, CommandError) as error:
            diagnostics.append({"code": "INTEGRITY_ERROR", "message": str(error)})
        return {"ok": not diagnostics, "schema_version": SCHEMA_VERSION, "checked": checked,
                "diagnostics": diagnostics, "evidence_class": "INTERNAL_REPLAY_AND_CAPTURED_BYTE_INTEGRITY",
                "limitations": ["Hash chains are not signatures or externally anchored proofs.",
                                "Replay consumes recorded experiment results; it does not re-run experiments or establish scientific truth."]}
