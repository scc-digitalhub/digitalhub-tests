from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh

if typing.TYPE_CHECKING:
    from digitalhub_runtime_python.entities.run._base.entity import RunPythonRun

p_name = "tutorial-project"
py_ver = "PYTHON3_10"
f_src = str(Path(__file__).parent / "src" / "functions.py")
w_src = str(Path(__file__).parent / "src" / "pipeline.py")


def run() -> None:
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
    api_func = project.new_function(
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

    api_func.refresh()
    run_serve_model = api_func.list_runs()[0]
    svc_url = f"http://{run_serve_model.status.service['url']}/?page=5&size=10"
    res: RunPythonRun = run_serve_model.invoke(url=svc_url)
    res.raise_for_status()
