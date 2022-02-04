import glob
import os
import re
import shutil
import sys
from pathlib import Path

_THIS_DIRNAME = os.path.dirname(__file__)
_PROTOS_PATH = os.path.abspath(
    os.path.join(_THIS_DIRNAME, "..", "protos", "ansys", "api", "fluent", "v0")
)
_PY_OUT_PATH = os.path.abspath(
    os.path.join(_THIS_DIRNAME, "..", "ansys", "api", "fluent", "v0")
)
_PACKAGE_NAME = "ansys.api.fluent.v0"


def build_python_grpc(protos_path=_PROTOS_PATH, out_path=_PY_OUT_PATH):
    """
    Builds *.py source interface files given a path containing *.protos
    files
    """
    shutil.rmtree(out_path, ignore_errors=True)
    Path.mkdir(Path(out_path), parents=True, exist_ok=True)
    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "cpp"

    # check for protos at the protos path
    proto_glob = os.path.join(protos_path, "*.proto")
    files = glob.glob(proto_glob, recursive=True)
    if not files:
        raise FileNotFoundError(
            f"Unable locate any *.proto files at {protos_path}"
        )

    # verify proto tools are installed
    try:
        import grpc_tools  # noqa: F401 # pylint: disable=unused-import
    except ImportError:
        raise ImportError(
            "Missing ``grpcio-tools`` package.\n"
            "Install with `pip install grpcio-tools`"
        )

    cmd = f"{sys.executable} -m grpc_tools.protoc -I{protos_path} "
    cmd += f"--python_out={out_path} --grpc_python_out={out_path} {proto_glob}"

    if os.system(cmd):
        raise RuntimeError(f"Failed to run:\n\n{cmd}")

    # verify something was built
    files = glob.glob(os.path.join(out_path, "*.py"), recursive=True)
    if not files:
        raise RuntimeError(f"No python source generated at {out_path}")

    # grab all module names and source
    py_glob = os.path.join(out_path, "*.py")
    grpc_source_files = glob.glob(py_glob, recursive=True)
    py_source = {}
    for filename in grpc_source_files:
        relative_path = filename.replace(out_path, "")
        module_name = ".".join(re.split(r"\\|/", relative_path))
        module_name = module_name.rstrip(".py")
        module_name = module_name.strip(".")
        py_source[module_name] = open(filename).read()

    # Replace all imports for each module with an absolute import with
    # the new full module name

    # For example
    # import variant_pb2 as variant__pb2
    # becomes...
    # import ansys.api.fluent.v0.variant_pb2 as variant__pb2
    for relative_module_name in py_source:
        # module on the root level
        module_name = relative_module_name
        find_str = f"import {module_name}"
        repl_str = f"import {_PACKAGE_NAME}.{module_name}"

        # search through all modules
        for mod_name, mod_source in py_source.items():
            py_source[mod_name] = mod_source.replace(find_str, repl_str)

    # write python source
    for module_name, module_source in py_source.items():
        relative_module_path = module_name.split(".")
        relative_module_path[-1] = f"{relative_module_path[-1]}.py"
        filename = os.path.join(out_path, *relative_module_path)

        with open(filename, "w") as f:
            f.write(module_source)


if __name__ == "__main__":
    build_python_grpc()