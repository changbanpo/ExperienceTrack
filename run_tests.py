#!/usr/bin/env python3
"""Simple test runner without coverage"""

import sys
import pytest

if __name__ == "__main__":
    # Run tests without coverage options
    sys.exit(pytest.main(["tests/test_core.py", "-v", "--no-header"]))
