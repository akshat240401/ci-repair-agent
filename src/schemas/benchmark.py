from typing import Literal
from pydantic import BaseModel, Field
FailureType = Literal["SYNTAX_ERROR","TYPE_ERROR","LOGIC_BUG","TEST_FAILURE","DEPENDENCY_ERROR","ENVIRONMENT_CONFIG","NETWORK_TIMEOUT","BUILD_ERROR","RESOURCE_FAILURE","UNKNOWN"]
class BenchmarkMetadata(BaseModel):
    case_id: str = Field(pattern=r"^case_\d{3}$")
    title: str
    language: Literal["python"]
    python_version: Literal["3.11"]
    failure_family: str
    expected_failure_type: FailureType
    targeted_test: str
    full_test_command: str = "pytest -q"
    repairable: bool = True
    challenging: bool = False
    notes: str = ""
