// chartRenderer.js
// Универсальный рендерер графиков для чата ImmoAssist
// Использует Chart.js (подключён через CDN)

/**
 * Рендерит график в указанный контейнер по данным из backend
 * @param {HTMLElement} container - DOM-элемент для вставки графика
 * @param {Object} chartData - Данные для графика (type, chartType, data, title, xLabel, yLabel, options)
 */
export function renderChart(container, chartData) {
    console.log('renderChart called with:', chartData);
    
    // Проверяем наличие Chart.js
    if (typeof Chart === 'undefined') {
        console.error('Chart.js не загружен!');
        container.innerHTML = '<div style="color: red; padding: 10px;">Ошибка: Chart.js не загружен</div>';
        return;
    }
    
    // Очищаем контейнер
    container.innerHTML = '';
    
    // Создаём обёртку для canvas с фиксированными размерами
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    wrapper.style.width = '100%';
    wrapper.style.height = '300px'; // Фиксированная высота
    container.appendChild(wrapper);
    
    // Создаём canvas
    const canvas = document.createElement('canvas');
    wrapper.appendChild(canvas);

    // Преобразуем данные для Chart.js
    let type = chartData.chartType || 'line';
    let data = {};
    let options = chartData.options || {};

    // Проверяем наличие данных
    if (!chartData.data || !Array.isArray(chartData.data) || chartData.data.length === 0) {
        console.error('Нет данных для отображения графика');
        container.innerHTML = '<div style="color: red; padding: 10px;">Нет данных для отображения</div>';
        return;
    }

    // Преобразование данных в зависимости от типа графика
    if (type === 'pie') {
        // Для pie chart нужны labels и data
        const labels = [];
        const values = [];
        
        chartData.data.forEach(item => {
            if (item.label && item.value !== undefined) {
                labels.push(item.label);
                values.push(item.value);
            } else if (item.name && item.amount !== undefined) {
                labels.push(item.name);
                values.push(item.amount);
            } else if (item.category && item.total !== undefined) {
                labels.push(item.category);
                values.push(item.total);
            }
        });
        
        data = {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ]
            }]
        };
    } else {
        // Для line/bar charts преобразуем данные в формат {x, y}
        let processedData = chartData.data.map(item => {
            // Поддержка разных форматов данных
            if (item.x !== undefined && item.y !== undefined) {
                return { x: item.x, y: item.y };
            } else if (item.year !== undefined && item.profitability !== undefined) {
                return { x: item.year, y: item.profitability };
            } else if (item.year !== undefined && item.yield !== undefined) {
                return { x: item.year, y: item.yield };
            } else if (item.month !== undefined && item.value !== undefined) {
                return { x: item.month, y: item.value };
            } else if (item.date !== undefined && item.amount !== undefined) {
                return { x: item.date, y: item.amount };
            } else {
                // Если структура неизвестна, пытаемся найти числовые поля
                const keys = Object.keys(item);
                if (keys.length >= 2) {
                    return { x: item[keys[0]], y: item[keys[1]] };
                }
            }
            return item;
        });

        // Сортируем по x для лучшего отображения
        processedData.sort((a, b) => a.x - b.x);

        // Проверяем, нужно ли использовать категориальную ось X
        const isNumericX = processedData.every(item => !isNaN(parseFloat(item.x)));
        
        if (!isNumericX) {
            // Для категориальных данных используем другой формат
            data = {
                labels: processedData.map(item => String(item.x)),
                datasets: [{
                    label: chartData.title || 'График',
                    data: processedData.map(item => item.y),
                    borderColor: '#36A2EB',
                    backgroundColor: type === 'bar' ? 'rgba(54, 162, 235, 0.5)' : 'rgba(54, 162, 235, 0.1)',
                    tension: 0.1
                }]
            };
        } else {
            // Для числовых данных
            data = {
                datasets: [{
                    label: chartData.title || 'График',
                    data: processedData,
                    borderColor: '#36A2EB',
                    backgroundColor: type === 'bar' ? 'rgba(54, 162, 235, 0.5)' : 'rgba(54, 162, 235, 0.1)',
                    tension: 0.1
                }]
            };
        }
    }

    // Опции
    options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { 
                display: type === 'pie',
                position: 'bottom'
            },
            title: {
                display: !!chartData.title,
                text: chartData.title || '',
                font: {
                    size: 16
                }
            }
        }
    };
    
    // Добавляем оси для line/bar charts
    if (type !== 'pie') {
        // Определяем тип оси X на основе данных
        const isNumericX = data.labels ? false : true;
        
        options.scales = {
            x: {
                type: isNumericX ? 'linear' : 'category',
                position: 'bottom',
                title: {
                    display: !!chartData.xLabel,
                    text: chartData.xLabel || ''
                }
            },
            y: {
                title: {
                    display: !!chartData.yLabel,
                    text: chartData.yLabel || ''
                },
                beginAtZero: true
            }
        };
    }
    
    // Объединяем с дополнительными опциями
    if (chartData.options) {
        options = { ...options, ...chartData.options };
    }

    console.log('Chart debug:', { type, data: data, options });

    try {
        // Создаём график
        const chart = new Chart(canvas, {
            type: type,
            data: data,
            options: options
        });
        
        console.log('Chart created successfully:', chart);
        
        // Добавляем обработчик для уничтожения графика при необходимости
        container.chartInstance = chart;
    } catch (error) {
        console.error('Error creating chart:', error);
        container.innerHTML = `<div style="color: red; padding: 10px;">Ошибка при создании графика: ${error.message}</div>`;
    }
} 