function getCssVariable(variableName) {
    return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
}

document.addEventListener('DOMContentLoaded', function() {
    const chartTextColor = getCssVariable('--text-main');
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
                        color: chartTextColor
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
                        color: chartTextColor
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
                        display: false, // Hide title
                        text: 'Date',
                        color: chartTextColor
                    },
                    ticks: {
                        display: false, // Hide ticks
                        color: chartTextColor
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Challenges Solved',
                        color: chartTextColor
                    },
                    ticks: {
                        color: chartTextColor
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
                                            color: chartTextColor
                                        }
                                    }
                                }        }
    });

    // Data for Challenges Solved Count Bar Chart
    const challengeSolveCountCanvas = document.getElementById('challengeSolveCountChart');
    const challengeSolveLabels = flaskChallengeSolveLabels; // Access global variable
    const challengeSolveValues = flaskChallengeSolveValues; // Access global variable
    const challengeSolveCountCtx = challengeSolveCountCanvas.getContext('2d');

    new Chart(challengeSolveCountCtx, {
        type: 'bar',
        data: {
            labels: challengeSolveLabels,
            datasets: [{
                label: 'Times Solved',
                data: challengeSolveValues,
                backgroundColor: '#4BC0C0', // A distinct color
                borderColor: '#4BC0C0',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y', // This makes it a horizontal bar chart
            responsive: true,
            plugins: {
                legend: {
                    display: false // Hide the legend
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Times Solved',
                        color: chartTextColor
                    },
                    ticks: {
                        color: chartTextColor
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Challenge',
                        color: chartTextColor
                    },
                    ticks: {
                        color: chartTextColor
                    }
                }
            }
        }
    });

    // Data for Global Points Over Time Chart (Admin View)
    const globalPointsOverTimeCanvas = document.getElementById('challengePointsOverTimeChart');
    const globalStatsOverTime = flaskGlobalStatsOverTime; // Access global variable
    const userScoresOverTime = flaskUserScoresOverTime; // Access global variable
    const globalPointsOverTimeCtx = globalPointsOverTimeCanvas.getContext('2d');

    if (globalStatsOverTime && globalStatsOverTime.length > 0) {
        const datasets = [];

        // Add global statistics lines
        datasets.push({
            label: 'Global Average Score',
            data: globalStatsOverTime.map(d => ({ x: d.x, y: d.avg })),
            borderColor: 'rgb(255, 0, 0)', // Red for average
            borderDash: [5, 5],
            tension: 0.1,
            fill: false,
            pointRadius: 0
        });

        datasets.push({
            label: 'Global Max Score',
            data: globalStatsOverTime.map(d => ({ x: d.x, y: d.max })),
            borderColor: 'rgb(0, 200, 0)', // Green for max
            borderDash: [2, 2],
            tension: 0.1,
            fill: false,
            pointRadius: 0
        });

        datasets.push({
            label: 'Global Min Score',
            data: globalStatsOverTime.map(d => ({ x: d.x, y: d.min })),
            borderColor: 'rgb(200, 0, 0)', // Dark Red for min
            borderDash: [2, 2],
            tension: 0.1,
            fill: false,
            pointRadius: 0
        });

        datasets.push({
            label: 'Global Q3 (75th Percentile)',
            data: globalStatsOverTime.map(d => ({ x: d.x, y: d.q3 })),
            borderColor: 'rgb(128, 0, 128)', // Purple for IQR
            borderDash: [2, 2],
            tension: 0.1,
            fill: '+1', // Fill to Q1
            backgroundColor: 'rgba(128, 0, 128, 0.1)',
            pointRadius: 0
        });
        datasets.push({
            label: 'Global Q1 (25th Percentile)',
            data: globalStatsOverTime.map(d => ({ x: d.x, y: d.q1 })),
            borderColor: 'rgb(128, 0, 128)', // Purple for IQR
            borderDash: [2, 2],
            tension: 0.1,
            fill: '-1', // Fill to the dataset below (nothing below, so fills to 0)
            backgroundColor: 'rgba(128, 0, 128, 0.1)',
            pointRadius: 0
        });

        // +1 Standard Deviation Band
        datasets.push({
            label: 'Global Avg +1 Std Dev',
            data: globalStatsOverTime.map(d => ({ x: d.x, y: d.avg + d.std_dev })),
            borderColor: 'rgb(255, 165, 0)', // Orange for std dev
            borderDash: [2, 2],
            tension: 0.1,
            fill: '+1', // Fill to the dataset below (average)
            backgroundColor: 'rgba(255, 165, 0, 0.1)',
            pointRadius: 0
        });

        // -1 Standard Deviation Band
        datasets.push({
            label: 'Global Avg -1 Std Dev',
            data: globalStatsOverTime.map(d => ({ x: d.x, y: d.avg - d.std_dev })),
            borderColor: 'rgb(255, 165, 0)', // Orange for std dev
            borderDash: [2, 2],
            tension: 0.1,
            fill: '-1', // Fill to the dataset below (nothing below, so fills to 0)
            backgroundColor: 'rgba(255, 165, 0, 0.1)',
            pointRadius: 0
        });

        // Add individual user scores
        const userColors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]; // A set of distinct colors
        let colorIndex = 0;

        for (const username in userScoresOverTime) {
            if (userScoresOverTime.hasOwnProperty(username)) {
                datasets.push({
                    label: username,
                    data: userScoresOverTime[username],
                    borderColor: userColors[colorIndex % userColors.length],
                    tension: 0.1,
                    fill: false,
                    pointRadius: 2,
                    pointHoverRadius: 5
                });
                colorIndex++;
            }
        }

        new Chart(globalPointsOverTimeCtx, {
            type: 'line',
            interaction: {
                mode: 'nearest',
                intersect: false,
                hitRadius: 20
            },
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: chartTextColor
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return context[0].label; // Show date as title
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2);
                                }
                                return label;
                            },
                            afterBody: function(context) {
                                // Find the global stats for the current timestamp
                                const currentTimestamp = context[0].parsed.x;
                                const globalStat = globalStatsOverTime.find(d => new Date(d.x).getTime() === currentTimestamp);
                                if (globalStat) {
                                    return [
                                        '', // Empty line for spacing
                                        '--- Global Statistics ---',
                                        `Min: ${globalStat.min.toFixed(2)}`,
                                        `Max: ${globalStat.max.toFixed(2)}`,
                                        `Avg: ${globalStat.avg.toFixed(2)}`,
                                        `Std Dev: ${globalStat.std_dev.toFixed(2)}`,
                                        `Q1: ${globalStat.q1.toFixed(2)}`,
                                        `Q3: ${globalStat.q3.toFixed(2)}`
                                    ];
                                }
                                return null;
                            }
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
                            color: chartTextColor
                        },
                        ticks: {
                            color: chartTextColor
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Score',
                            color: chartTextColor
                        },
                        ticks: {
                            color: chartTextColor
                        }
                    }
                }
            }
        });
    }
});