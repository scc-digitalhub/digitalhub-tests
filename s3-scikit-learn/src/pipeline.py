from digitalhub_runtime_hera.dsl import step
from hera.workflows import DAG, Workflow


def pipeline():
    with Workflow(entrypoint="dag") as w:
        with DAG(name="dag"):
            A0 = step(
                template={"action": "build"},
                function="prepare-data",
            )
            A1 = step(
                template={"action": "job"},
                function="prepare-data",
                outputs=["dataset"],
            )
            B0 = step(
                template={"action": "build"},
                function="train-classifier",
            )
            B1 = step(
                template={
                    "action": "job",
                    "inputs": {"di": "{{inputs.parameters.di}}"},
                },
                function="train-classifier",
                inputs={"di": A1.get_parameter("dataset")},
            )
            C = step(template={"action": "serve"}, function="serve-classifier")
            [A0, B0] >> A1 >> B1 >> C
    return w
