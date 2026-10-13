from digitalhub_runtime_hera.dsl import step
from hera.workflows import DAG, Workflow


def pipeline():
    with Workflow(entrypoint="dag") as w, DAG(name="dag"):
        A = step(
            template={"action": "build"},
            function="sklearn-train-classifier",
        )
        B = step(
            template={"action": "job"},
            function="sklearn-train-classifier",
            outputs=["dataset"],
        )
        C = step(
            template={
                "action": "job",
                "inputs": {"di": "{{inputs.parameters.di}}"},
            },
            function="train-classifier",
            inputs={"di": B.get_parameter("dataset")},
        )
        D = step(template={"action": "serve"}, function="serve-classifier")
        A >> B >> C >> D
    return w
