from artifact import TestArtifactCRUD
from dataitem import TestDataitemCRUD
from function import TestFunctionCRUD
from model import TestModelCRUD
from run import TestRunCRUD
from secret import TestSecretCRUD
from task import TestTaskCRUD
from trigger import TestTriggerCRUD
from workflow import TestWorkflowCRUD

TEST_CLASSES = [
    (TestArtifactCRUD, "TestArtifactCRUD"),
    (TestDataitemCRUD, "TestDataitemCRUD"),
    (TestModelCRUD, "TestModelCRUD"),
    (TestSecretCRUD, "TestSecretCRUD"),
    (TestFunctionCRUD, "TestFunctionCRUD"),
    (TestRunCRUD, "TestRunCRUD"),
    (TestTaskCRUD, "TestTaskCRUD"),
    (TestWorkflowCRUD, "TestWorkflowCRUD"),
    (TestTriggerCRUD, "TestTriggerCRUD"),
]
