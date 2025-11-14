from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
import numpy as np

if typing.TYPE_CHECKING:
    from digitalhub_runtime_modelserve.entities.run.sklearnserve_run.entity import (
        RunSklearnserveRun,
    )

p_name = "tutorial-project"
f_src = str(Path(__file__).parent / "src" / "functions.py")
w_src = str(Path(__file__).parent / "src" / "pipeline.py")


def run() -> None:
    """
    Run a test pipeline.
    """
    project = dh.get_or_create_project(p_name)

    _ = project.new_function(
        name="prepare-data",
        kind="python",
        python_version="PYTHON3_10",
        code_src=f_src,
        handler="data_generator",
    )
    train_fn = project.new_function(
        name="train-classifier",
        kind="python",
        python_version="PYTHON3_10",
        code_src=f_src,
        handler="train_model",
        requirements=["numpy<2"],
    )
    workflow = project.new_workflow(
        name="ml-pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )

    workflow.run("build", wait=True)
    workflow.run("pipeline", wait=True)

    train_fn.refresh()
    run_train_fn = train_fn.list_runs()[0]

    model = run_train_fn.output("model")
    serve_func = project.new_function(
        name="serve-classifier",
        kind="sklearnserve",
        path=model.key,
    )

    serve_run: RunSklearnserveRun = serve_func.run("serve", wait=True)

    data = np.random.rand(2, 30).tolist()
    json_payload = {
        "inputs": [
            {
                "name": "input-0",
                "shape": [2, 30],
                "datatype": "FP32",
                "data": data,
            }
        ]
    }

    result = serve_run.invoke(json=json_payload)
    result.raise_for_status()
