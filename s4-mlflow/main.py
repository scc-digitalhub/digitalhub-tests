from __future__ import annotations

import os
import time
import typing
from pathlib import Path

import digitalhub as dh

if typing.TYPE_CHECKING:
    from digitalhub.entities.model.mlflow.entity import ModelMlflow
    from digitalhub_runtime_modelserve.entities.run.mlflowserve_serve_run.entity import (
        RunMlflowserveServeRun,
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

    train_fn = project.new_function(
        name="train-mlflow-model",
        kind="python",
        python_version="PYTHON3_10",
        code_src=f_src,
        handler="train_model",
        requirements=["numpy<2", "mlflow<3", "scikit-learn <= 1.6.1"],
    )

    serve_func = project.new_function(
        name="serve-mlflow-model",
        kind="mlflowserve",
        path=f"store://{p_name}/models/iris-classifier",
        model_name="iris-classifier",
    )

    workflow = project.new_workflow(
        name="mlflow-pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )

    workflow.run("build", wait=True)
    workflow.run("pipeline", wait=True)

    time.sleep(45)  # wait for the service to be ready

    data = [
        [5.1, 3.5, 1.4, 0.2],
        [4.9, 3.0, 1.4, 0.2],
        [4.7, 3.2, 1.3, 0.2],
        [4.6, 3.1, 1.5, 0.2],
        [5.0, 3.6, 1.4, 0.2],
        [5.4, 3.9, 1.7, 0.4],
        [4.6, 3.4, 1.4, 0.3],
        [5.0, 3.4, 1.5, 0.2],
        [4.4, 2.9, 1.4, 0.2],
        [4.9, 3.1, 1.5, 0.1],
    ]
    json_payload = {
        "inputs": [
            {
                "name": "input-0",
                "shape": [-1, 4],
                "datatype": "FP64",
                "data": data,
            }
        ]
    }

    model: ModelMlflow = train_fn.list_runs()[0].output("model")
    serve_run: RunMlflowserveServeRun = serve_func.list_runs()[0]
    try:
        result = serve_run.invoke(model_name=model.name, json=json_payload)
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
