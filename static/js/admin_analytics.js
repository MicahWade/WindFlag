document.addEventListener('DOMContentLoaded', function() {
    // Data for Category Points Chart
    const categoryCanvas = document.getElementById('categoryPointsChart');
    const categoryLabels = flaskCategoryLabels; // Access global variable
    const categoryValues = flaskCategoryValues; // Access global variable
    const categoryCtx = categoryCanvas.getContext('2d');

    new Chart(categoryCtx, {
        type: 'pie',
        data: {
            labels: categoryLabels,
            datasets: [{
                data: categoryValues,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
                    '#E7E9ED', '#8AC926', '#FFCA3A', '#1982C4', '#6A4C93', '#F45B69'
                ],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: 'white' // Set legend text color to white
                    }
                }
            }
        }
    });

    // Data for User Points Chart
    const userCanvas = document.getElementById('userPointsChart');
    const userLabels = flaskUserLabels; // Access global variable
    const userValues = flaskUserValues; // Access global variable
    const userCtx = userCanvas.getContext('2d');

    new Chart(userCtx, {
        type: 'pie',
        data: {
            labels: userLabels,
            datasets: [{
                data: userValues,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
                    '#E7E9ED', '#8AC926', '#FFCA3A', '#1982C4', '#6A4C93', '#F45B69'
                ],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false // Hide the legend
                }
            }
        }
    });

    // Data for Challenges Solved Over Time Chart
    const challengesSolvedCanvas = document.getElementById('challengesSolvedChart');
    const solvedDates = flaskSolvedDates; // Access global variable
    const solvedCounts = flaskSolvedCounts; // Access global variable
    const challengesSolvedCtx = challengesSolvedCanvas.getContext('2d');

    new Chart(challengesSolvedCtx, {
        type: 'line',
        interaction: {
            mode: 'nearest',
            intersect: false, // Allow tooltip to activate when near a data point
            hitRadius: 20 // Increased hit radius for tooltip activation
        },
        interaction: {
            mode: 'nearest',
            intersect: false, // Allow tooltip to activate when near a data point
            hitRadius: 20 // Increased hit radius for tooltip activation
        },
        data: {
            labels: solvedDates,
            datasets: [{
                label: 'Challenges Solved',
                data: solvedCounts,
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: 'white'
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        tooltipFormat: 'MMM d, yyyy',
                        displayFormats: {
                            day: 'MMM d'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Date',
                        color: 'white'
                    },
                    ticks: {
                        color: 'white'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Challenges Solved',
                        color: 'white'
                    },
                    ticks: {
                        color: 'white'
                    }
                }
            }
        }
    });

    // Data for Fails vs Succeeds Chart
    const failsSucceedsCanvas = document.getElementById('failsSucceedsChart');
    const failsSucceedsLabels = flaskFailsSucceedsLabels; // Access global variable
    const failsSucceedsValues = flaskFailsSucceedsValues; // Access global variable
    const failsSucceedsCtx = failsSucceedsCanvas.getContext('2d');

    new Chart(failsSucceedsCtx, {
        type: 'pie',
        data: {
            labels: failsSucceedsLabels,
            datasets: [{
                data: failsSucceedsValues,
                backgroundColor: [
                    '#4CAF50', // Green for Succeeds
                    '#F44336'  // Red for Fails
                ],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: 'white'
                    }
                }
            }
        }
    });
});