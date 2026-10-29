// Runs Python (Pyodide) off the main thread so long simulations never freeze the page.
// Messages in:  {id, type: "init" | "run" | "runFile" | "saveModule" | "test" | "resetNamespace", ...}
// Messages out: {id, ok, text, images, error}

const PYODIDE_VERSION = "0.28.3";
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
importScripts(INDEX_URL + "pyodide.js");

const BOOTSTRAP = `
import base64, importlib, io, linecache, os, sys, traceback, warnings
os.environ["MPLBACKEND"] = "Agg"
warnings.filterwarnings("ignore", message=".*non-interactive.*")
HOME = "/home/pyodide"
if HOME not in sys.path:
    sys.path.insert(0, HOME)
_NAMESPACES = {}

def _purge_package():
    # Forget imported library and test modules so edited files are re-read from disk.
    for name in list(sys.modules):
        if name.split(".")[0] in ("finance101", "tests") or name.startswith("test_"):
            del sys.modules[name]
    importlib.invalidate_caches()

def _figures():
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is None:
        return []
    images = []
    for num in plt.get_fignums():
        buf = io.BytesIO()
        plt.figure(num).savefig(buf, format="png", dpi=110, bbox_inches="tight")
        images.append(base64.b64encode(buf.getvalue()).decode())
    plt.close("all")
    return images

def _format_exception(exc):
    tb = exc.__traceback__
    # Hide Pyodide's own frames; start at the first frame of user code.
    while tb is not None and not (tb.tb_frame.f_code.co_filename == "<cell>"
                                  or tb.tb_frame.f_code.co_filename.startswith(HOME)):
        tb = tb.tb_next
    return "".join(traceback.format_exception(type(exc), exc, tb))

def _run(code, key=None, filename="<cell>"):
    from pyodide.code import eval_code
    if key:
        scope = _NAMESPACES.setdefault(key, {"__name__": "__main__"})
    else:
        scope = {"__name__": "__main__", "__file__": filename}
    if filename == "<cell>":
        # Lets tracebacks show the offending line of the cell.
        linecache.cache[filename] = (len(code), None, code.splitlines(True), filename)
    out = io.StringIO()
    saved = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = out
    ok = True
    try:
        result = eval_code(code, scope, filename=filename)
        if result is not None:
            print(repr(result))
    except SystemExit:
        pass
    except BaseException as exc:
        ok = False
        out.write(_format_exception(exc))
    finally:
        sys.stdout, sys.stderr = saved
    return {"ok": ok, "text": out.getvalue(), "images": _figures()}

def _save_module(path, code):
    with open(path, "w") as f:
        f.write(code)
    _purge_package()
    module = path[len(HOME) + 1:-3].replace("/", ".")
    return _run(f"import {module}\\nprint('Saved and reloaded {module}')", None, "<cell>")

def _test(paths):
    import pytest
    _purge_package()
    out = io.StringIO()
    saved = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = out
    try:
        code = pytest.main(["-q", "--capture=sys", "-p", "no:cacheprovider", "--color=no", *paths])
    finally:
        sys.stdout, sys.stderr = saved
    return {"ok": int(code) == 0, "text": out.getvalue(), "images": []}
`;

let pyodide = null;

async function init(baseUrl) {
  pyodide = await loadPyodide({ indexURL: INDEX_URL });
  const manifest = await (await fetch(baseUrl + "manifest.json")).json();
  for (const [folder, files] of Object.entries(manifest.files)) {
    pyodide.FS.mkdirTree(`/home/pyodide/${folder}`);
    await Promise.all(files.map(async (path) => {
      const text = await (await fetch(baseUrl + path)).text();
      pyodide.FS.writeFile(`/home/pyodide/${path}`, text);
    }));
  }
  pyodide.runPython(BOOTSTRAP);
  return { ok: true, text: `Python ${pyodide.runPython("import sys; sys.version.split()[0]")} ready` };
}

function toJs(proxy) {
  const value = proxy.toJs({ dict_converter: Object.fromEntries });
  proxy.destroy();
  return value;
}

async function handle(msg) {
  switch (msg.type) {
    case "init":
      return init(msg.baseUrl);
    case "run":
      await pyodide.loadPackagesFromImports(msg.code);
      return toJs(pyodide.globals.get("_run")(msg.code, msg.namespace || null, "<cell>"));
    case "runFile": {
      const path = `/home/pyodide/${msg.path}`;
      pyodide.FS.writeFile(path, msg.code);
      await pyodide.loadPackagesFromImports(msg.code);
      pyodide.globals.get("_purge_package")();
      return toJs(pyodide.globals.get("_run")(msg.code, null, path));
    }
    case "saveModule":
      return toJs(pyodide.globals.get("_save_module")(`/home/pyodide/${msg.path}`, msg.code));
    case "test": {
      await pyodide.loadPackage("pytest");
      if (msg.path && msg.code != null) pyodide.FS.writeFile(`/home/pyodide/${msg.path}`, msg.code);
      const paths = pyodide.toPy(msg.path ? [`/home/pyodide/${msg.path}`] : ["/home/pyodide/tests"]);
      return toJs(pyodide.globals.get("_test")(paths));
    }
    case "resetNamespace":
      pyodide.runPython(`_NAMESPACES.pop(${JSON.stringify(msg.namespace)}, None)`);
      return { ok: true, text: "" };
    default:
      throw new Error(`unknown message type ${msg.type}`);
  }
}

// Messages are handled one at a time, in order, like cells in a notebook.
let queue = Promise.resolve();
self.onmessage = (event) => {
  const msg = event.data;
  queue = queue.then(async () => {
    try {
      self.postMessage({ id: msg.id, images: [], ...(await handle(msg)) });
    } catch (err) {
      self.postMessage({ id: msg.id, ok: false, text: String(err && err.message || err), images: [] });
    }
  });
};
