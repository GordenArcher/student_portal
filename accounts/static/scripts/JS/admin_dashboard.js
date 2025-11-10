const dateElement = document.getElementById("current-date");
const now = new Date();

const options = { year: "numeric", month: "long", day: "numeric" };

dateElement.textContent = now.toLocaleDateString("en-US", options);


const performanceCtx = document.getElementById('performanceChart').getContext('2d');
new Chart(performanceCtx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
        datasets: [{
            label: 'Average Score',
            data: [72, 74, 73, 76, 78, 77, 79, 81, 80, 82, 78.5],
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6
        }, {
            label: 'Attendance Rate',
            data: [88, 90, 89, 91, 93, 92, 94, 95, 94, 96, 94.2],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: {
                    color: '#e2e8f0'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

const classCtx = document.getElementById('classChart').getContext('2d');
new Chart(classCtx, {
    type: 'doughnut',
    data: {
        labels: ['JHS 1', 'JHS 2', 'JHS 3'],
        datasets: [{
            data: [450, 412, 422],
            backgroundColor: ['#2563eb', '#10b981', '#8b5cf6'],
            borderWidth: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
});

const subjectCtx = document.getElementById('subjectChart').getContext('2d');
new Chart(subjectCtx, {
    type: 'bar',
    data: {
        labels: ['Math', 'English', 'Science', 'Social St.', 'ICT', 'French'],
        datasets: [{
            label: 'Average Score',
            data: [82.5, 79.3, 76.8, 73.2, 85.1, 78.9],
            backgroundColor: '#2563eb',
            borderRadius: 6
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: {
                    color: '#e2e8f0'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});