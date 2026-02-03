import os
import time
import typing
from pathlib import Path

import digitalhub as dh

if typing.TYPE_CHECKING:
    from digitalhub_runtime_container.entities.run._base.entity import RunContainerRun

p_name = os.environ.get("PROJECT_NAME", "digitalhub-tests")
BASE_DIR = (Path(__file__).parent).relative_to(Path.cwd())
w_src = str(BASE_DIR / "src" / "pipeline.py")


def main() -> None:
    """
    Run a test pipeline.
    """
    project = dh.get_or_create_project(p_name)

    _ = project.new_function(
        kind="container",
        name="c-job",
        image="hello-world:latest",
    )

    _ = project.new_function(
        kind="container",
        name="c-build",
        base_image="python:3.11-slim",
    )

    serve_func = project.new_function(
        kind="container",
        name="c-serve",
        image="hashicorp/http-echo:latest",
    )

    workflow = project.new_workflow(
        name="container-pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )

    workflow.run("build", wait=True)
    workflow.run(
        "pipeline",
        wait=True,
    )

    serve_func.refresh()
    serve_run: RunContainerRun = serve_func.list_runs()[0]
    time.sleep(20)  # wait for the service to be ready
    try:
        result = serve_run.invoke()
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
