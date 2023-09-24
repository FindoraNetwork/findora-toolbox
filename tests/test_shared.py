import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath("."))

import pytest
from src.shared import compare_two_files


def test_compare_two_files():
    # Create two temporary files
    with tempfile.NamedTemporaryFile(delete=False) as f1, tempfile.NamedTemporaryFile(delete=False) as f2:
        # Write some content to the files
        f1.write(b"Test content")
        f2.write(b"Test content")

        # Test with identical files
        assert compare_two_files(f1.name, f2.name) == True

        # Modify one file
        with open(f2.name, "w") as f:
            f.write("Different content")

        # Test with different files
        assert compare_two_files(f1.name, f2.name) == False

    # Clean up temporary files
    os.remove(f1.name)
    os.remove(f2.name)
