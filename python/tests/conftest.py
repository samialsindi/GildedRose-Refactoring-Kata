"""
ApprovalTests requires a GUI diff tool. We do not have one.
approvaltests-use-reporter did not work.

Overriding this after the plugin configures itself.

"""

import pytest
from approvaltests import set_default_reporter
from approvaltests.reporters import PythonNativeReporter


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    set_default_reporter(PythonNativeReporter())