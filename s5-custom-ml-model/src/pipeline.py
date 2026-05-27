from digitalhub_runtime_hera.dsl import step
from hera.workflows import DAG, Workflow


def pipeline():
    with Workflow(entrypoint="dag") as w:
        with DAG(name="dag"):
            Build1 = step(
                template={"action": "build"},
                function="train-time-series-model",
            )
            Build2 = step(
                template={"action": "build"},
                function="serve-time-series-model",
            )
            A = step(
                template={"action": "job"},
                function="train-time-series-model",
                outputs=["model"],
            )
            B = step(
                template={
                    "action": "serve",
                    "init_parameters": {"model_key": "{{inputs.parameters.model}}"},
                },
                function="serve-time-series-model",
                inputs={"model": A.get_parameter("model")},
            )
            [Build1, Build2] >> A >> B
    return w
