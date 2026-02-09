from __future__ import annotations

import os
import sys
import time
import typing
from pathlib import Path

import digitalhub as dh

if typing.TYPE_CHECKING:
    from digitalhub_runtime_python.entities.run._base.entity import RunPythonRun

sys.path.append(str(Path(__file__).resolve().parents[1]))
from logging_utils import configure_logging

p_name = os.environ.get("PROJECT_NAME", "digitalhub-tests")
py_ver = "PYTHON3_10"
BASE_DIR = (Path(__file__).parent).relative_to(Path.cwd())
f_src = str(BASE_DIR / "src" / "functions.py")
w_src = str(BASE_DIR / "src" / "pipeline.py")
logger = configure_logging(__name__)


def main() -> None:
    """
    Run a test pipeline.
    """
    project = dh.get_or_create_project(p_name)

    url = "https://opendata.comune.bologna.it/api/explore/v2.1/catalog/datasets/rilevazione-flusso-veicoli-tramite-spire-anno-2023/exports/csv?limit=10000&lang=it&timezone=Europe%2FRome&use_labels=true&delimiter=%3B"
    di = project.new_dataitem(
        name="url-data-item",
        kind="table",
        path=url,
    )
    _ = project.new_function(
        name="download-data",
        kind="python",
        python_version=py_ver,
        code_src=f_src,
        handler="downloader",
    )
    _ = project.new_function(
        name="process-spire",
        kind="python",
        python_version=py_ver,
        code_src=f_src,
        handler="process_spire",
    )
    _ = project.new_function(
        name="process-measures",
        kind="python",
        python_version=py_ver,
        code_src=f_src,
        handler="process_measures",
    )
    serve_func = project.new_function(
        name="api",
        kind="python",
        python_version=py_ver,
        code_src=f_src,
        handler="serve",
        init_function="init_context",
    )
    workflow = project.new_workflow(
        name="pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )
    workflow.run("build", wait=True)
    workflow.run(
        "pipeline",
        parameters={"url": di.key},
        wait=True,
    )

    serve_func.refresh()
    serve_run: RunPythonRun = serve_func.list_runs()[0]
    svc_url = f"http://{serve_run.status.service['url']}/?page=5&size=10"
    time.sleep(20)  # wait for the service to be ready
    result = None
    try:
        result = serve_run.invoke(url=svc_url)
        result.raise_for_status()
        dh.delete_run(serve_run.key)
        logger.info("Request succeeded: %s", result.json())
    except Exception as e:
        logger.exception("Request failed: %s", e)
        if result is not None:
            logger.info("Response content: %s", result.text)
        dh.delete_run(serve_run.key)
        raise e


if __name__ == "__main__":
    main()
