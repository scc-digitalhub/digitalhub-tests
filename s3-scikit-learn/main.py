from __future__ import annotations

import os
import time
import typing
from pathlib import Path

import digitalhub as dh
import numpy as np

if typing.TYPE_CHECKING:
    from digitalhub.entities.model.sklearn.entity import ModelSklearn
    from digitalhub_runtime_modelserve.entities.run.sklearnserve_run.entity import (
        RunSklearnserveRun,
    )

p_name = os.environ.get("PROJECT_NAME", "digitalhub-tests")
BASE_DIR = (Path(__file__).parent).relative_to(Path.cwd())
f_src = str(BASE_DIR / "src" / "functions.py")
w_src = str(BASE_DIR / "src" / "pipeline.py")


def main() -> None:
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
        requirements=["numpy<2", "scikit-learn<1.8"],
    )
    train_fn = project.new_function(
        name="train-classifier",
        kind="python",
        python_version="PYTHON3_10",
        code_src=f_src,
        handler="train_model",
        requirements=["numpy<2", "scikit-learn<1.8"],
    )

    serve_func = project.new_function(
        name="serve-classifier",
        kind="sklearnserve",
    )

    workflow = project.new_workflow(
        name="ml-pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )

    workflow.run("build", wait=True)
    workflow.run("pipeline", wait=True)

    time.sleep(45)  # wait for the service to be ready

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

    model: ModelSklearn = train_fn.list_runs()[0].output("model")
    serve_run: RunSklearnserveRun = serve_func.list_runs()[0]
    result = serve_run.invoke(model_name=model.name, json=json_payload)
    try:
        result.raise_for_status()
        dh.delete_run(serve_run.key)
        print("Request succeeded:", result.json())
    except Exception as e:
        print("Request failed:", e)
        print("Response content:", result.text)
        dh.delete_run(serve_run.key)
        raise e


if __name__ == "__main__":
    main()
