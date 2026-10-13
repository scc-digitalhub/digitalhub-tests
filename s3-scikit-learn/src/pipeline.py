from digitalhub_runtime_hera.dsl import step
from hera.workflows import DAG, Workflow


def pipeline():
    with Workflow(entrypoint="dag") as w, DAG(name="dag"):
        A0 = step(
            template={"action": "build"},
            function="prepare-data",
        )
        B0 = step(
            template={"action": "build"},
            function="train-classifier",
        )
        A = step(
            template={"action": "job"},
            function="prepare-data",
            outputs=["dataset"],
        )
        B = step(
            template={
                "action": "job",
                "inputs": {"di": "{{inputs.parameters.di}}"},
            },
            function="train-classifier",
            inputs={"di": A.get_parameter("dataset")},
        )
        C = step(template={"action": "serve"}, function="serve-classifier")
        [A0, B0] >> A >> B >> C
    return w
