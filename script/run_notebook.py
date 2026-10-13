"""Thực thi notebook từ kernel sạch bằng đúng Python đang chạy chương trình này."""

import os
import sys
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[1]
    for variable, directory in {
        "IPYTHONDIR": "ipython",
        "JUPYTER_RUNTIME_DIR": "jupyter_runtime",
        "JUPYTER_CONFIG_DIR": "jupyter_config",
        "JUPYTER_DATA_DIR": "jupyter_data",
        "MPLCONFIGDIR": "matplotlib",
    }.items():
        location = root / ".cache" / directory
        location.mkdir(parents=True, exist_ok=True)
        os.environ[variable] = str(location)
    path = root / "notebook" / "bai06.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    client = NotebookClient(notebook, km=manager, timeout=180,
                            resources={"metadata": {"path": str(root)}})
    client.execute()
    errors = [out for cell in notebook.cells if cell.cell_type == "code"
              for out in cell.outputs if out.output_type == "error"]
    if errors:
        raise RuntimeError(f"Notebook còn {len(errors)} output lỗi.")
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    count = sum(cell.cell_type == "code" for cell in notebook.cells)
    print(f"Đã thực thi và lưu {count} cell code, không có lỗi: {path}")


if __name__ == "__main__":
    main()
