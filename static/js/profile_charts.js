document.addEventListener('DOMContentLoaded', function() {
    // Function to create a line/bar chart
    function createChart(ctx, type, data, options) {
        new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });
    }

    // 1. Points Over Time Chart
    const pointsOverTimeDataElement = document.getElementById('points-over-time-data');
    if (pointsOverTimeDataElement) {
        const pointsOverTimeData = JSON.parse(pointsOverTimeDataElement.textContent);
        if (pointsOverTimeData && pointsOverTimeData.length > 0) {
            const ctx = document.getElementById('pointsOverTimeChart').getContext('2d');
            createChart(ctx, 'line', {
                datasets: [{
                    label: 'Cumulative Score',
                    data: pointsOverTimeData,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Score'
                        }
                    }
                }
            });
        } else {
            document.getElementById('pointsOverTimeChartContainer').innerHTML = '<p class="text-gray-400 text-center">No submissions yet to display points over time.</p>';
        }
    }

    // 2. Fails vs. Succeeds Chart
    const failsVsSucceedsDataElement = document.getElementById('fails-vs-succeeds-data');
    if (failsVsSucceedsDataElement) {
        const failsVsSucceedsData = JSON.parse(failsVsSucceedsDataElement.textContent);
        if (failsVsSucceedsData && failsVsSucceedsData.values.some(v => v > 0)) { // Check if there's any data
            const ctx = document.getElementById('failsVsSucceedsChart').getContext('2d');
            createChart(ctx, 'pie', {
                labels: failsVsSucceedsData.labels,
                datasets: [{
                    data: failsVsSucceedsData.values,
                    backgroundColor: [
                        'rgb(75, 192, 75)',  // Succeeds (Green)
                        'rgb(255, 99, 132)'  // Fails (Red)
                    ],
                    hoverOffset: 4
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
            });
        } else {
            document.getElementById('failsVsSucceedsChartContainer').innerHTML = '<p class="text-gray-400 text-center">No flag attempts yet to display fails vs. succeeds.</p>';
        }
    }

    // 3. Categories per Score Chart
    const categoriesPerScoreDataElement = document.getElementById('categories-per-score-data');
    if (categoriesPerScoreDataElement) {
        const categoriesPerScoreData = JSON.parse(categoriesPerScoreDataElement.textContent);
        if (categoriesPerScoreData && categoriesPerScoreData.values.some(v => v > 0)) {
            const ctx = document.getElementById('categoriesPerScoreChart').getContext('2d');
            createChart(ctx, 'pie', { // Changed to pie chart
                labels: categoriesPerScoreData.labels,
                datasets: [{
                    label: 'Points per Category',
                    data: categoriesPerScoreData.values,
                    backgroundColor: [ // Added colors for pie chart
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(153, 102, 255)',
                        'rgb(255, 159, 64)'
                    ],
                    hoverOffset: 4 // Added hover effect
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
            });
        } else {
            document.getElementById('categoriesPerScoreChartContainer').innerHTML = '<p class="text-gray-400 text-center">No solved challenges yet to display points per category.</p>';
        }
    }

    // 4. Challenges Complete Chart
    const challengesCompleteDataElement = document.getElementById('challenges-complete-data');
    if (challengesCompleteDataElement) {
        const challengesCompleteData = JSON.parse(challengesCompleteDataElement.textContent);
        if (challengesCompleteData && challengesCompleteData.length > 0) {
            const ctx = document.getElementById('challengesCompleteChart').getContext('2d');
            createChart(ctx, 'line', {
                datasets: [{
                    label: 'Challenges Solved',
                    data: challengesCompleteData,
                    borderColor: 'rgb(255, 159, 64)',
                    tension: 0.1,
                    fill: false
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Challenges'
                        },
                        ticks: {
                            stepSize: 1 // Ensure integer ticks for challenge count
                        }
                    }
                }
            });
        } else {
            document.getElementById('challengesCompleteChartContainer').innerHTML = '<p class="text-gray-400 text-center">No challenges solved yet to display challenges complete over time.</p>';
        }
    }
});
