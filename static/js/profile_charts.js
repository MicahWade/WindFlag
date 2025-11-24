document.addEventListener('DOMContentLoaded', function() {
    const computedStyle = getComputedStyle(document.body);

    // Fetch CSS variables for chart colors
    const chartColors = [];
    for (let i = 1; i <= 10; i++) {
        const color = computedStyle.getPropertyValue(`--chart-color-${i}`).trim();
        if (color) chartColors.push(color);
    }
    // Fetch CSS variables for specific chart elements
    const chartColorSucceeds = computedStyle.getPropertyValue('--chart-color-succeeds').trim();
    const chartColorFails = computedStyle.getPropertyValue('--chart-color-fails').trim();
    const chartColorAverage = computedStyle.getPropertyValue('--chart-color-average').trim();
    const chartColorMax = computedStyle.getPropertyValue('--chart-color-max').trim();
    const chartColorMin = computedStyle.getPropertyValue('--chart-color-min').trim();
    const chartColorIqr = computedStyle.getPropertyValue('--chart-color-iqr').trim();
    const chartColorStdDev = computedStyle.getPropertyValue('--chart-color-std-dev').trim();
    const chartColorChallengesComplete = computedStyle.getPropertyValue('--chart-color-challenges-complete').trim();

    // Fetch CSS variables for category colors
    const categoryColorStart = computedStyle.getPropertyValue('--category-color-start').trim();
    const categoryColorGeneralSkills = computedStyle.getPropertyValue('--category-color-general-skills').trim();
    const categoryColorWebExploitation = computedStyle.getPropertyValue('--category-color-web-exploitation').trim();
    const categoryColorCryptography = computedStyle.getPropertyValue('--category-color-cryptography').trim();
    const categoryColorReverseEngineering = computedStyle.getPropertyValue('--category-color-reverse-engineering').trim();
    const categoryColorForensics = computedStyle.getPropertyValue('--category-color-forensics').trim();
    const categoryColorPwn = computedStyle.getPropertyValue('--category-color-pwn').trim();
    const categoryColorMiscellaneous = computedStyle.getPropertyValue('--category-color-miscellaneous').trim();
    const categoryColorUncategorized = computedStyle.getPropertyValue('--category-color-uncategorized').trim();

    // Fetch CSS variables for text colors
    const textMuted = computedStyle.getPropertyValue('--text-muted').trim();

    // Function to create a line/bar chart
    function createChart(ctx, type, data, options) {
        // Destroy existing chart instance if it exists
        if (Chart.getChart(ctx)) {
            Chart.getChart(ctx).destroy();
        }
        // Register the annotation plugin if it's available
        if (window.ChartAnnotation) {
            Chart.register(window.ChartAnnotation);
        }
        new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });
    }

    // 1. Points Over Time Chart
    const profileStatsDataElement = document.getElementById('profile-stats-data');
    const profileChartsDataElement = document.getElementById('profile-charts-data'); // New element

    if (profileChartsDataElement) {
        const profileStatsData = profileStatsDataElement ? JSON.parse(profileStatsDataElement.textContent) : {};
        const profileChartsData = profileChartsDataElement ? JSON.parse(profileChartsDataElement.textContent) : {}; // New data

        const targetUserScoreHistory = profileChartsData.target_user_score_history;
        const globalStatsOverTime = profileChartsData.global_stats_over_time;

        if (targetUserScoreHistory && targetUserScoreHistory.length > 0) {
            const ctx = document.getElementById('pointsOverTimeChart').getContext('2d');

            // Define a color palette for categories (this part remains for the cumulative score line)
            const categoryColors = {
                'Start': categoryColorStart || 'rgb(128, 128, 128)', // Grey for initial point
                'General Skills': categoryColorGeneralSkills || 'rgb(255, 99, 132)',
                'Web Exploitation': categoryColorWebExploitation || 'rgb(54, 162, 235)',
                'Cryptography': categoryColorCryptography || 'rgb(255, 205, 86)',
                'Reverse Engineering': categoryColorReverseEngineering || 'rgb(75, 192, 192)',
                'Forensics': categoryColorForensics || 'rgb(153, 102, 255)',
                'Pwn': categoryColorPwn || 'rgb(255, 159, 64)',
                'Miscellaneous': categoryColorMiscellaneous || 'rgb(201, 203, 207)',
                'Uncategorized': categoryColorUncategorized || 'rgb(100, 100, 100)'
                // Add more colors for other categories as needed
            };

            const datasets = [{
                label: 'User Score',
                data: targetUserScoreHistory,
                borderColor: chartColorChallengesComplete || 'rgb(75, 192, 192)', // Using challenges complete color for user score line
                tension: 0.1,
                fill: false,
                pointBackgroundColor: targetUserScoreHistory.map(point => categoryColors[point.category] || 'rgb(0, 0, 0)'), // Color nodes by category
                pointRadius: 5, // Make points visible
                pointHoverRadius: 7
            }];

            // Add global statistics lines
            if (globalStatsOverTime && globalStatsOverTime.length > 0) {
                datasets.push({
                    label: 'Average Score',
                    data: globalStatsOverTime.map(d => ({
                        x: d.x,
                        y: d.avg
                    })),
                    borderColor: chartColorAverage || 'rgb(255, 0, 0)', // Red for average
                    borderDash: [5, 5],
                    tension: 0.1,
                    fill: false,
                    pointRadius: 0
                });

                datasets.push({
                    label: 'Max Score',
                    data: globalStatsOverTime.map(d => ({
                        x: d.x,
                        y: d.max
                    })),
                    borderColor: chartColorMax || 'rgb(0, 200, 0)', // Green for max
                    borderDash: [2, 2],
                    tension: 0.1,
                    fill: false,
                    pointRadius: 0
                });

                datasets.push({
                    label: 'Min Score',
                    data: globalStatsOverTime.map(d => ({
                        x: d.x,
                        y: d.min
                    })),
                    borderColor: chartColorMin || 'rgb(200, 0, 0)', // Dark Red for min
                    borderDash: [2, 2],
                    tension: 0.1,
                    fill: false,
                    pointRadius: 0
                });

                datasets.push({
                    label: 'Q3',
                    data: globalStatsOverTime.map(d => ({
                        x: d.x,
                        y: d.q3
                    })),
                    borderColor: chartColorIqr || 'rgb(128, 0, 128)', // Purple for IQR
                    borderDash: [2, 2],
                    tension: 0.1,
                    fill: '+1', // Fill to Q1
                    backgroundColor: chartColorIqr ? chartColorIqr.replace('rgb(', 'rgba(').replace(')', `, 0.1)`) : 'rgba(128, 0, 128, 0.1)',
                    pointRadius: 0
                });

                datasets.push({
                    label: 'Q1',
                    data: globalStatsOverTime.map(d => ({
                        x: d.x,
                        y: d.q1
                    })),
                    borderColor: chartColorIqr || 'rgb(128, 0, 128)', // Purple for IQR
                    borderDash: [2, 2],
                    tension: 0.1,
                    fill: '-1', // Fill to the dataset below (nothing below, so fills to 0)
                    backgroundColor: chartColorIqr ? chartColorIqr.replace('rgb(', 'rgba(').replace(')', `, 0.1)`) : 'rgba(128, 0, 128, 0.1)',
                    pointRadius: 0
                });

                // +1 Standard Deviation Band
                datasets.push({
                    label: '+1 Std Dev',
                    data: globalStatsOverTime.map(d => ({
                        x: d.x,
                        y: d.avg + d.std_dev
                    })),
                    borderColor: chartColorStdDev || 'rgb(255, 165, 0)', // Orange for std dev
                    borderDash: [2, 2],
                    tension: 0.1,
                    fill: '+1', // Fill to the dataset below (average)
                    backgroundColor: chartColorStdDev ? chartColorStdDev.replace('rgb(', 'rgba(').replace(')', `, 0.1)`) : 'rgba(255, 165, 0, 0.1)',
                    pointRadius: 0
                });

                // -1 Standard Deviation Band
                datasets.push({
                    label: '-1 Std Dev',
                    data: globalStatsOverTime.map(d => ({
                        x: d.x,
                        y: d.avg - d.std_dev
                    })),
                    borderColor: chartColorStdDev || 'rgb(255, 165, 0)', // Orange for std dev
                    borderDash: [2, 2],
                    tension: 0.1,
                    fill: '-1', // Fill to the dataset below (nothing below, so fills to 0)
                    backgroundColor: chartColorStdDev ? chartColorStdDev.replace('rgb(', 'rgba(').replace(')', `, 0.1)`) : 'rgba(255, 165, 0, 0.1)',
                    pointRadius: 0
                });
            }

            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'nearest',
                    intersect: false,
                    hitRadius: 20
                },
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
                        min: 0, // Ensure the y-axis always starts at 0
                        title: {
                            display: true,
                            text: 'Score'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                if (context[0].dataset.label === 'User Score') {
                                    return context[0].label; // Show date as title for User Score
                                }
                                return null; // Hide title for other datasets
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label === 'User Score') {
                                    if (context.parsed.y !== null) {
                                        label += ': ' + context.parsed.y;
                                    }
                                    return label;
                                }
                                return null; // Hide other labels
                            }
                        }
                    },
                    annotation: {
                        annotations: {} // Clear annotations
                    }
                }
            };

            // Remove annotations for Max, Min, IQR as they are now dynamic lines
            // The tooltip will still show the overall stats.
            // No need to modify chartOptions.plugins.annotation.annotations here.
            // The previous annotations for Max, Min, IQR are removed.
            // The tooltip will still show the overall stats.

            createChart(ctx, 'line', {
                datasets: datasets
            }, chartOptions);
        } else {
            document.getElementById('pointsOverTimeChartContainer').innerHTML = '<p class="theme-profile-text-muted text-center">No submissions yet to display points over time.</p>';
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
                        chartColorSucceeds || 'rgb(75, 192, 75)', // Succeeds (Green)
                        chartColorFails || 'rgb(255, 99, 132)' // Fails (Red)
                    ],
                    hoverOffset: 4
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
            });
        } else {
            document.getElementById('failsVsSucceedsChartContainer').innerHTML = '<p class="theme-profile-text-muted text-center">No flag attempts yet to display fails vs. succeeds.</p>';
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
                    backgroundColor: chartColors.length > 0 ? chartColors.slice(0, categoriesPerScoreData.values.length) : [ // Added colors for pie chart
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
            document.getElementById('categoriesPerScoreChartContainer').innerHTML = '<p class="theme-profile-text-muted text-center">No solved challenges yet to display points per category.</p>';
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
                    borderColor: chartColorChallengesComplete || 'rgb(255, 159, 64)',
                    tension: 0.1,
                    fill: false
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
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
            document.getElementById('challengesCompleteChartContainer').innerHTML = '<p class="theme-profile-text-muted text-center">No challenges solved yet to display challenges complete over time.</p>';
        }
    }
});