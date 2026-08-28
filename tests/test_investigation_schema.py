from src.schemas.investigation import InvestigationResult, ToolRequest


def _result(scope, files):
    return InvestigationResult(
        root_cause="contract drift",
        evidence=["evidence"],
        target_files=files,
        recommended_change_scope=scope,
        confidence=0.95,
    )


def test_tool_request_schema():
    req = ToolRequest(
        action="tool",
        tool="search_symbol",
        arguments={"symbol": "build_config"},
        reason="find implementation",
    )
    assert req.tool == "search_symbol"


def test_canonical_values_stay_canonical():
    assert _result("single_file", ["src/a.py"]).recommended_change_scope == "single_file"
    assert _result(
        "multi_file", ["src/a.py", "src/b.py"]
    ).recommended_change_scope == "multi_file"


def test_common_multi_file_aliases_normalize():
    aliases = [
        "cross_file_contract",
        "cross-file",
        "multi-file",
        "multiple files",
        "two_files",
        "two files",
        "cross_module_change",
    ]
    for alias in aliases:
        assert _result(
            alias, ["src/a.py", "src/b.py"]
        ).recommended_change_scope == "multi_file"


def test_common_single_file_aliases_normalize():
    aliases = ["single-file", "single file", "one_file", "one file"]
    for alias in aliases:
        assert _result(
            alias, ["src/a.py"]
        ).recommended_change_scope == "single_file"


def test_unknown_scope_falls_back_to_target_file_count():
    assert _result(
        "coordinated contract repair",
        ["src/a.py", "src/b.py"],
    ).recommended_change_scope == "multi_file"

    assert _result(
        "localized implementation change",
        ["src/a.py"],
    ).recommended_change_scope == "single_file"


def test_scope_is_derived_even_if_model_omits_it():
    result = InvestigationResult.model_validate(
        {
            "action": "final",
            "root_cause": "contract drift",
            "evidence": ["evidence"],
            "target_files": ["src/a.py", "src/b.py"],
            "confidence": 0.9,
        }
    )
    assert result.recommended_change_scope == "multi_file"
