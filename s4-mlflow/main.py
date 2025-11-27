from __future__ import annotations

import time
import typing
from pathlib import Path

import digitalhub as dh
from sklearn import datasets

if typing.TYPE_CHECKING:
    from digitalhub_runtime_modelserve.entities.run.mlflowserve_run.entity import (
        RunMlflowserveRun,
    )

p_name = "digitalhub-tests"
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

    workflow = project.new_workflow(
        name="mlflow-pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )

    workflow.run("build", wait=True)
    workflow.run("pipeline", wait=True)

    train_fn.refresh()
    train_model_run = train_fn.list_runs()[0]
    model = train_model_run.output("model")
    serve_func = project.new_function(
        name="serve-mlflow-model",
        kind="mlflowserve",
        model_name=model.name,
        path=model.key,
    )
    serve_run: RunMlflowserveRun = serve_func.run("serve", wait=True)

    iris = datasets.load_iris()
    data = iris.data[0:2].tolist()
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
    time.sleep(45)  # wait for the service to be ready
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
