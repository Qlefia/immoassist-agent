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
ImmoAssist Multi-Agent System - Enterprise Edition

Production-ready agent system for German real estate investment consulting,
built with Google ADK following enterprise architecture best practices.
"""

# Import root agent for ADK Web interface
from . import agent

# Version info
__version__ = "3.0.0"
__description__ = "Enterprise multi-agent system for German real estate investments"

# Export for ADK Web interface
__all__ = ["root_agent"] 