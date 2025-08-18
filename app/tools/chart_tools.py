from google.adk.tools import FunctionTool
from typing import List, Dict, Any, Optional

@FunctionTool
# Chart creation tool for ImmoAssist frontend visualization

def create_chart(
    chart_type: str,
    data: List[Dict[str, Any]],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generates chart structure for frontend rendering using Chart.js.

    Args:
        chart_type: Chart type (line, bar, pie, etc.)
        data: List of data points. Supported formats:
              - [{"label": "2024", "value": 3.5}, ...] - standard format
              - [{"x": "2024", "y": 3.5}, ...] - Chart.js format
              - [{"year": 2024, "yield": 3.5}, ...] - custom format (will be converted)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        options: Additional options (colors, legend, etc.)
    Returns:
        Chart structure for frontend with type and Chart.js parameters
    """
    if options is None:
        options = {}
    
    # Transform data to correct format for Chart.js
    processed_data = []
    if chart_type in ['bar', 'line'] and data:
        for item in data:
            # Standard format with label/value
            if 'label' in item and 'value' in item:
                processed_data.append({
                    "x": str(item['label']),
                    "y": item['value']
                })
            # Chart.js format - already correct
            elif 'x' in item and 'y' in item:
                processed_data.append(item)
            # Custom formats - try to detect and convert
            elif 'year' in item and 'yield' in item:
                processed_data.append({
                    "x": str(item['year']),
                    "y": item['yield']
                })
            # Generic fallback - use first two keys
            elif len(item) >= 2:
                keys = list(item.keys())
                processed_data.append({
                    "x": str(item[keys[0]]),
                    "y": item[keys[1]]
                })
            else:
                processed_data.append(item)
    else:
        processed_data = data
    
    return {
        "type": "chart",
        "chartType": chart_type,
        "title": title,
        "xLabel": x_label,
        "yLabel": y_label,
        "data": processed_data,
        "options": options
    } 