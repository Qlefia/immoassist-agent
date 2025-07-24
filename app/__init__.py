# Copyright 2025 ImmoAssist
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ImmoAssist - AI-powered German Real Estate Investment Assistant.

A multi-agent system providing comprehensive support for real estate 
investment decisions in the German market, including property search,
financial analysis, legal guidance, and market insights.
"""

from .agent import root_agent
from .config import config

# Version info
__version__ = "1.0.0"
__author__ = "ImmoAssist Team"

# Main agent export for Google ADK
agent = root_agent

# Public API
__all__ = ["agent", "root_agent", "config"]
