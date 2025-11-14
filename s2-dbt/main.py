from pathlib import Path

import digitalhub as dh

p_name = "tutorial-project"
f_src = str(Path(__file__).parent / "src" / "functions.py")
w_src = str(Path(__file__).parent / "src" / "pipeline.py")


def run() -> None:
    """
    Run a test pipeline.
    """
    project = dh.get_or_create_project(p_name)

    url = "https://gist.githubusercontent.com/kevin336/acbb2271e66c10a5b73aacf82ca82784/raw/e38afe62e088394d61ed30884dd50a6826eee0a8/employees.csv"
    di = project.new_dataitem(
        name="employees-data",
        kind="table",
        path=url,
    )

    sql = """
    WITH tab AS (
        SELECT  *
        FROM    {{ ref('employees') }}
    )
    SELECT  *
    FROM    tab
    WHERE   tab."DEPARTMENT_ID" = '50'
    """

    func = project.new_function(
        name="transform-employees",
        kind="dbt",
        code=sql,
    )

    workflow = project.new_workflow(
        name="dbt-pipeline",
        kind="hera",
        code_src=w_src,
        handler="pipeline",
    )

    workflow.run("build", wait=True)
    workflow.run(
        "pipeline",
        parameters={"employees": di.key},
        wait=True,
    )
