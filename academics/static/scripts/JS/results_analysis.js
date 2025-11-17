import showToast from "/static/scripts/JS/admin_d.js"

document.addEventListener('DOMContentLoaded', function() {
    initializeAnalysisCharts();
    initializeAnalysisFilters();
    initializeAnalysisEventListeners();
});

function initializeAnalysisCharts() {
    // Wait a bit to ensure DOM is fully ready
    setTimeout(() => {
        createGradeDistributionChart();
        createSubjectPerformanceChart();
        createClassPerformanceChart();
        createPerformanceTrendsChart();
    }, 100);
}

function initializeAnalysisFilters() {
    // Real-time filter updates
    const filterForm = document.querySelector('.filters-form');
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                // Add a small delay to prevent too many requests
                clearTimeout(window.analysisFilterTimeout);
                window.analysisFilterTimeout = setTimeout(() => {
                    filterForm.submit();
                }, 800);
            });
        });
    }
}

function createGradeDistributionChart() {
    const ctx = document.getElementById('gradeDistributionChart');
    if (!ctx) return;

    // Get data from the template (you would pass this from Django)
    const gradeData = getGradeDistributionData();
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: gradeData.labels,
            datasets: [{
                label: 'Number of Students',
                data: gradeData.data,
                backgroundColor: [
                    '#10b981', // A+ - Green
                    '#10b981', // A - Green
                    '#3b82f6', // B+ - Blue
                    '#3b82f6', // B - Blue
                    '#f59e0b', // C+ - Orange
                    '#f59e0b', // C - Orange
                    '#f59e0b', // D+ - Orange
                    '#ef4444', // D - Red
                    '#ef4444', // E - Red
                    '#ef4444'  // F - Red
                ],
                borderColor: [
                    '#0f9668', '#0f9668', '#2563eb', '#2563eb',
                    '#d97706', '#d97706', '#d97706', '#dc2626',
                    '#dc2626', '#dc2626'
                ],
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Grade Distribution',
                    font: {
                        size: 16,
                        weight: '600'
                    },
                    padding: 20
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y} students`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Students',
                        font: {
                            weight: '600'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Grades',
                        font: {
                            weight: '600'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

function createSubjectPerformanceChart() {
    const ctx = document.getElementById('subjectPerformanceChart');
    if (!ctx) return;

    const subjectData = getSubjectPerformanceData();
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: subjectData.labels,
            datasets: [{
                label: 'Average Score',
                data: subjectData.data,
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3b82f6',
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#3b82f6',
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Subject Performance Comparison',
                    font: {
                        size: 16,
                        weight: '600'
                    },
                    padding: 20
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.r}%`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 11,
                            weight: '600'
                        },
                        color: '#374151'
                    },
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'transparent',
                        color: '#64748b',
                        font: {
                            size: 10
                        }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

function createClassPerformanceChart() {
    const ctx = document.getElementById('classPerformanceChart');
    if (!ctx) return;

    const classData = getClassPerformanceData();
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: classData.labels,
            datasets: [
                {
                    label: 'Average Score',
                    data: classData.scores,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 4,
                    order: 2
                },
                {
                    label: 'Pass Rate',
                    data: classData.passRates,
                    type: 'line',
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    order: 1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Class Performance Comparison',
                    font: {
                        size: 16,
                        weight: '600'
                    },
                    padding: 20
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(1) + '%';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Average Score (%)',
                        font: {
                            weight: '600'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y1: {
                    beginAtZero: true,
                    max: 100,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Pass Rate (%)',
                        font: {
                            weight: '600'
                        }
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            animation: {
                duration: 1200,
                easing: 'easeOutQuart'
            }
        }
    });
}

function createPerformanceTrendsChart() {
    const ctx = document.getElementById('performanceTrendsChart');
    if (!ctx) return;

    const trendData = getPerformanceTrendsData();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.periods,
            datasets: [
                {
                    label: 'Mathematics',
                    data: trendData.math,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'English',
                    data: trendData.english,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Science',
                    data: trendData.science,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#f59e0b',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Overall Average',
                    data: trendData.overall,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    borderWidth: 4,
                    borderDash: [5, 5],
                    pointBackgroundColor: '#8b5cf6',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Performance Trends Over Time',
                    font: {
                        size: 16,
                        weight: '600'
                    },
                    padding: 20
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Average Score (%)',
                        font: {
                            weight: '600'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Academic Period',
                        font: {
                            weight: '600'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Data functions - In a real app, this data would come from Django
function getGradeDistributionData() {
    // This would be populated from Django context
    // For now, using sample data
    return {
        labels: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'E', 'F'],
        data: [15, 42, 68, 55, 38, 25, 18, 12, 8, 5]
    };
}

function getSubjectPerformanceData() {
    return {
        labels: ['Mathematics', 'English', 'Science', 'Social Studies', 'ICT', 'French', 'Creative Arts', 'PE'],
        data: [85, 78, 82, 75, 88, 70, 80, 85]
    };
}

function getClassPerformanceData() {
    return {
        labels: ['JHS 1A', 'JHS 1B', 'JHS 2A', 'JHS 2B', 'JHS 3A', 'JHS 3B', 'SHS 1', 'SHS 2'],
        scores: [78.5, 82.3, 75.8, 80.2, 85.6, 79.1, 83.4, 87.2],
        passRates: [85, 88, 82, 86, 92, 84, 89, 94]
    };
}

function getPerformanceTrendsData() {
    return {
        periods: ['Term 1 2023', 'Term 2 2023', 'Term 3 2023', 'Term 1 2024', 'Term 2 2024', 'Term 3 2024'],
        math: [75, 78, 82, 80, 85, 88],
        english: [72, 75, 78, 76, 80, 82],
        science: [78, 80, 82, 81, 83, 85],
        overall: [75, 77, 80, 79, 82, 85]
    };
}

// Export functionality
function initializeAnalysisEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshDataBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshAnalysisData);
    }
    
    // Export options
    const exportOptions = document.querySelectorAll('.export-option');
    exportOptions.forEach(option => {
        option.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            exportAnalysis(format);
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + P for print
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            printAnalysisReport();
        }
        
        // Ctrl + R for refresh
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            refreshAnalysisData();
        }
        
        // Ctrl + E for export (opens dropdown)
        if (e.ctrlKey && e.key === 'e') {
            e.preventDefault();
            const exportBtn = document.getElementById('exportDropdownBtn');
            if (exportBtn) {
                exportBtn.click();
            }
        }
    });
}

// Remove the old refreshAnalysisData function and replace with this:
async function refreshAnalysisData() {
    const refreshBtn = document.getElementById('refreshDataBtn');
    if (!refreshBtn) return;
    
    const originalHtml = refreshBtn.innerHTML;
    refreshBtn.innerHTML = '<span class="loading-spinner"></span> Refreshing...';
    refreshBtn.disabled = true;
    
    try {
        // Get current filters
        const filters = getCurrentFilters();
        let refreshUrl = window.location.pathname;
        
        // Add current filters to refresh URL
        const params = new URLSearchParams();
        Object.keys(filters).forEach(key => {
            if (filters[key]) {
                params.append(key, filters[key]);
            }
        });
        
        if (params.toString()) {
            refreshUrl += '?' + params.toString();
        }
        
        // Reload the page with current filters
        window.location.href = refreshUrl;
        
    } catch (error) {
        console.error('Error refreshing data:', error);
        showToast('Error refreshing data', 'error');
        refreshBtn.innerHTML = originalHtml;
        refreshBtn.disabled = false;
    }
}

// Update the exportAnalysis function to use the new approach
async function exportAnalysis(format = 'pdf') {
    const filters = getCurrentFilters();
    let exportUrl = `/academics/results/analysis/export/?format=${format}`;
    
    Object.keys(filters).forEach(key => {
        if (filters[key]) {
            exportUrl += `&${key}=${filters[key]}`;
        }
    });
    
    // Show loading state on all export buttons
    const exportOptions = document.querySelectorAll('.export-option');
    const exportDropdownBtn = document.getElementById('exportDropdownBtn');
    const originalTexts = [];
    
    exportOptions.forEach(btn => {
        originalTexts.push(btn.innerHTML);
        btn.innerHTML = '<span class="loading-spinner"></span> Exporting...';
        btn.disabled = true;
    });
    
    if (exportDropdownBtn) {
        const originalDropdownText = exportDropdownBtn.innerHTML;
        exportDropdownBtn.innerHTML = '<span class="loading-spinner"></span> Exporting...';
        exportDropdownBtn.disabled = true;
    }
    
    try {
        const response = await fetch(exportUrl);
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        const timestamp = new Date().toISOString().slice(0, 10);
        const filename = `results_analysis_${timestamp}.${format}`;
        a.download = filename;
        
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast(`${format.toUpperCase()} report exported successfully`, 'success');
        
    } catch (error) {
        console.error('Export error:', error);
        showToast(`Export failed: ${error.message}`, 'error');
    } finally {
        // Restore buttons
        exportOptions.forEach((btn, index) => {
            btn.innerHTML = originalTexts[index];
            btn.disabled = false;
        });
        
        if (exportDropdownBtn) {
            exportDropdownBtn.innerHTML = '<i class="bi bi-download"></i> Export Report';
            exportDropdownBtn.disabled = false;
        }
        
        // Close dropdown after export
        const dropdown = document.querySelector('.dropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }
}


function getCurrentFilters() {
    const urlParams = new URLSearchParams(window.location.search);
    const filters = {};
    
    for (const [key, value] of urlParams) {
        filters[key] = value;
    }
    
    return filters;
}

// Chart resize handler
function handleChartResize() {
    const charts = [
        'gradeDistributionChart',
        'subjectPerformanceChart', 
        'classPerformanceChart',
        'performanceTrendsChart'
    ];
    
    charts.forEach(chartId => {
        const chart = chart.getChart(chartId);
        if (chart) {
            chart.resize();
        }
    });
}

// Add resize listener
window.addEventListener('resize', handleChartResize);

// Print functionality
function printAnalysisReport() {
    const originalTitle = document.title;
    document.title = 'Academic Results Analysis Report - ' + new Date().toLocaleDateString();
    
    window.print();
    
    // Restore original title
    setTimeout(() => {
        document.title = originalTitle;
    }, 1000);
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + P for print
    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        printAnalysisReport();
    }
    
    // Ctrl + R for refresh
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        refreshAnalysisData();
    }
    
    // Ctrl + E for export
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        exportAnalysis('pdf');
    }
});

// Initialize tooltips for chart elements
function initializeChartTooltips() {
    const chartContainers = document.querySelectorAll('.chart-container');
    
    chartContainers.forEach(container => {
        container.addEventListener('mouseenter', function() {
            this.style.cursor = 'crosshair';
        });
        
        container.addEventListener('mouseleave', function() {
            this.style.cursor = 'default';
        });
    });
}

// Enhanced data validation
function validateChartData(data) {
    if (!data || typeof data !== 'object') {
        console.error('Invalid chart data provided');
        return false;
    }
    
    // Check for required properties based on chart type
    const requiredProps = {
        'gradeDistribution': ['labels', 'data'],
        'subjectPerformance': ['labels', 'data'],
        'classPerformance': ['labels', 'scores', 'passRates'],
        'performanceTrends': ['periods', 'math', 'english', 'science', 'overall']
    };
    
    return true; // Simplified validation
}

// Performance monitoring
function monitorChartPerformance() {
    const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
            if (entry.entryType === 'measure') {
                console.log(`Chart ${entry.name} took ${entry.duration}ms to render`);
            }
        });
    });
    
    observer.observe({ entryTypes: ['measure'] });
}

// Initialize performance monitoring in development
monitorChartPerformance();

window.ResultsAnalysis = {
    refreshData: refreshAnalysisData,
    exportReport: exportAnalysis,
    printReport: printAnalysisReport,
    initializeCharts: initializeAnalysisCharts
};