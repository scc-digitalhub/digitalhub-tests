from __future__ import annotations

import os
import time
import typing
from pathlib import Path

import digitalhub as dh

if typing.TYPE_CHECKING:
    from digitalhub_runtime_python.entities.run._base.entity import RunPythonRun

p_name = os.environ.get("PROJECT_NAME", "digitalhub-tests")
BASE_DIR = (Path(__file__).parent).relative_to(Path.cwd())
f_src = str(BASE_DIR / "src" / "functions.py")
w_src = str(BASE_DIR / "src" / "pipeline.py")


def main() -> None:
    """
    Run a test pipeline.
    """
    project = dh.get_or_create_project(p_name)

    build_func = project.new_function(
        name="build-time-series-model",
        kind="python",
        python_version="PYTHON3_10",
        code="placeholder",  # No build function needed
        handler="placeholder",
        requirements=["torch<2.6.0", "darts==0.30.0", "patsy"],
    )
    build_func.run("build", wait=True)
    build_func.refresh()

    _ = project.new_function(
        name="train-time-series-model",
        kind="python",
        python_version="PYTHON3_10",
        code_src=f_src,
        handler="train_model",
        image=build_func.spec.image,
    )
    serve_func = project.new_function(
        name="serve-time-series-model",
        kind="python",
        python_version="PYTHON3_10",
        code_src=f_src,
        handler="serve_predictions",
        init_function="init_context",
        image=build_func.spec.image,
    )
    workflow = project.new_workflow(
        name="time-series-pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )

    workflow.run("build", wait=True)
    workflow.run("pipeline", wait=True)

    serve_func.refresh()
    serve_run: RunPythonRun = serve_func.list_runs()[0]

    inputs = {
        "inference_input": [
            {"value": 360.0, "date": -347155200000.0},
            {"value": 342.0, "date": -344476800000.0},
            {"value": 406.0, "date": -342057600000.0},
            {"value": 396.0, "date": -339379200000.0},
            {"value": 420.0, "date": -336787200000.0},
            {"value": 472.0, "date": -334108800000.0},
            {"value": 548.0, "date": -331516800000.0},
            {"value": 559.0, "date": -328838400000.0},
            {"value": 463.0, "date": -326160000000.0},
            {"value": 407.0, "date": -323568000000.0},
            {"value": 362.0, "date": -320889600000.0},
            {"value": 405.0, "date": -318297600000.0},
            {"value": 417.0, "date": -315619200000.0},
            {"value": 391.0, "date": -312940800000.0},
            {"value": 419.0, "date": -310435200000.0},
            {"value": 461.0, "date": -307756800000.0},
            {"value": 472.0, "date": -305164800000.0},
            {"value": 535.0, "date": -302486400000.0},
            {"value": 622.0, "date": -299894400000.0},
            {"value": 606.0, "date": -297216000000.0},
            {"value": 508.0, "date": -294537600000.0},
            {"value": 461.0, "date": -291945600000.0},
            {"value": 390.0, "date": -289267200000.0},
            {"value": 432.0, "date": -286675200000.0},
        ]
    }
    time.sleep(45)  # wait for the service to be ready
    result = serve_run.invoke(json=inputs)
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
