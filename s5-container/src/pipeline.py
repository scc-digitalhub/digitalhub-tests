from digitalhub_runtime_hera.dsl import step
from hera.workflows import DAG, Workflow


def pipeline():
    with Workflow(entrypoint="dag") as w:
        with DAG(name="dag"):
            A = step(
                template={
                    "action": "job",
                    "run_as_user": "8877",
                },
                function="c-job",
            )
            B = step(
                template={
                    "action": "build",
                    "instructions": ["RUN apt-get update && apt-get install -y git"],
                },
                function="c-build",
            )
            C = step(
                template={
                    "action": "serve",
                    "replicas": 2,
                    "service_ports": [{"port": 5678, "target_port": 5678}],
                    "service_name": "http-echo",
                    "run_as_user": "8877",
                },
                function="c-serve",
            )
            A >> B >> C

    return w
