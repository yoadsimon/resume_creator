#!/usr/bin/env python3
"""Test basic resume generation functionality."""

import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to the system path to allow imports from src
sys.path.append(str(Path(__file__).parent.parent))

from src.core.resume_generator import ResumeGenerator
from src.data.consts import TEMP_DIR
from src.utils.open_ai import OpenAIClient
from src.utils.chat_utils import save_to_temp_file

# ... existing code ... 