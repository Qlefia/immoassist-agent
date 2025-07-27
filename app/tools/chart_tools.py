from google.adk.tools import FunctionTool
from typing import List, Dict, Any, Optional

@FunctionTool
# Переименовано для соответствия промптам и LLM

def create_chart(
    chart_type: str,
    data: List[Dict[str, Any]],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Генерирует структуру для построения графика на фронте через Chart.js.

    Args:
        chart_type: Тип графика (line, bar, pie и т.д.)
        data: Список точек/серий данных
        title: Заголовок графика
        x_label: Подпись оси X
        y_label: Подпись оси Y
        options: Дополнительные опции (цвета, легенда и т.д.)
    Returns:
        Структура для фронта с типом chart и параметрами для Chart.js
    """
    if options is None:
        options = {}
    return {
        "type": "chart",
        "chartType": chart_type,
        "title": title,
        "xLabel": x_label,
        "yLabel": y_label,
        "data": data,
        "options": options
    } 