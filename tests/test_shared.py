import sys
import os
import tempfile
import time

sys.path.insert(0, os.path.abspath("."))

import pytest
from unittest import mock
from unittest.mock import patch
from src.shared import compare_two_files, ask_yes_no, get_file_size, format_size, download_progress_hook


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


def test_ask_yes_no():
    # Test when user inputs 'y'
    with patch("builtins.input", return_value="y"):
        assert ask_yes_no("Would you like to continue?") == True

    # Test when user inputs 'yes'
    with patch("builtins.input", return_value="yes"):
        assert ask_yes_no("Would you like to continue?") == True

    # Test when user inputs 'n'
    with patch("builtins.input", return_value="n"):
        assert ask_yes_no("Would you like to continue?") == False

    # Test when user inputs 'no'
    with patch("builtins.input", return_value="no"):
        assert ask_yes_no("Would you like to continue?") == False

    # Test when user inputs an invalid option, followed by a valid option
    with patch("builtins.input", side_effect=["maybe", "y"]):
        assert ask_yes_no("Would you like to continue?") == True


def test_get_file_size():
    # Mocking a URL and its corresponding file size
    url = "https://easynode.pro/robots.txt"
    file_size = 67
    with patch("src.shared.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.info.return_value.__getitem__.return_value = str(file_size)
        assert get_file_size(url) == file_size

    # Testing with an invalid URL
    with pytest.raises(ValueError):
        get_file_size("invalid_url")


def test_format_size():
    assert format_size(1023) == "1023.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1048576) == "1.00 MB"
    assert format_size(1073741824) == "1.00 GB"


# Define start_time as a global variable
start_time = time.time()


def test_download_progress_hook(capfd):
    # Mock time.time to return different values on subsequent calls
    with mock.patch("src.shared.time.time", side_effect=[1234567890, 1234567891]):
        # Initialize start_time by calling the function with count equal to 0
        download_progress_hook(0, 1024, 4096)

        # Call the function again with the desired count value
        download_progress_hook(1, 1024, 4096)

    # Capture the output
    out, err = capfd.readouterr()

    # Assert the printed output is as expected
    assert (
        "Downloaded 1.00 KB of 4.00 KB (25%). Speed: 1.00 KB/s. Elapsed Time: 0h 0m 1s. Time remaining: 0h 0m 3s.                    \r"
        in out
    )
