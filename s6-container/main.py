import os
import sys
import time
import typing
from pathlib import Path

import digitalhub as dh

if typing.TYPE_CHECKING:
    from digitalhub_runtime_container.entities.run._base.entity import RunContainerRun

sys.path.append(str(Path(__file__).resolve().parents[1]))
from logging_utils import configure_logging

p_name = os.environ.get("PROJECT_NAME", "digitalhub-tests")
BASE_DIR = (Path(__file__).parent).relative_to(Path.cwd())
w_src = str(BASE_DIR / "src" / "pipeline.py")
logger = configure_logging(__name__)


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
    result = None
    try:
        result = serve_run.invoke()
        result.raise_for_status()
        dh.delete_run(serve_run.key)
        logger.info("Request succeeded: %s", result.text)
    except Exception as e:
        logger.exception("Request failed: %s", e)
        if result is not None:
            logger.info("Response content: %s", result.text)
        dh.delete_run(serve_run.key)
        raise e


if __name__ == "__main__":
    main()
