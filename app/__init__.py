"""
ImmoAssist - AI-powered German real estate investment assistant.

This package provides intelligent consultation services for German real estate
investments using advanced AI agents and multi-modal capabilities.
"""

from __future__ import annotations

# Apply Windows Path compatibility patch for Google ADK
import pathlib
from pathlib import WindowsPath

# Patch WindowsPath to support rstrip method
if not hasattr(WindowsPath, 'rstrip'):
    def rstrip(self, chars=None):
        """Add rstrip method to WindowsPath for compatibility with Google ADK."""
        return str(self).rstrip(chars)
    
    WindowsPath.rstrip = rstrip

__version__ = "0.1.0"
__author__ = "ImmoAssist Team"
__email__ = "team@immoassist.com"

# Public API exports
__all__ = [
    "__author__",
    "__email__",
    "__version__",
]
