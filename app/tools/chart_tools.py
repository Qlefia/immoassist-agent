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
        data: List of data points in format [{"value": number, "label": string}, ...]
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
        # For bar and line charts use format {x: label, y: value}
        for item in data:
            if 'value' in item and 'label' in item:
                processed_data.append({
                    "x": item['label'],  # Category/label for X-axis
                    "y": item['value']   # Value for Y-axis
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