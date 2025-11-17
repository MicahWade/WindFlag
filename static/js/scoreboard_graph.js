document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/scoreboard_data')
        .then(response => response.json())
        .then(data => {
            renderScoreboardGraph(data.top_players_history);
            populatePlayerRankings(data.all_players_ranked);
        })
        .catch(error => console.error('Error fetching scoreboard data:', error));

    function renderScoreboardGraph(topPlayersHistory) {
        const ctx = document.getElementById('scoreboardChart').getContext('2d');
        
        if (!topPlayersHistory || topPlayersHistory.length === 0) {
            ctx.font = '18px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available for graph.', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }

        // Extract unique player names
        const playerNames = Array.from(new Set(topPlayersHistory.flatMap(entry => Object.keys(entry.scores))));
        
        // --- Frontend Interpolation Logic ---
        const interpolatedPlayerHistory = {};
        const interpolationSteps = 10; // Number of steps for gradual increase
        const interpolationDurationMs = 60 * 1000; // 1 minute for interpolation

        playerNames.forEach(playerName => {
            interpolatedPlayerHistory[playerName] = [];
            let previousScore = 0;
            let previousTimestamp = null; // Will be set after the first point

            // Sort history by timestamp to ensure correct processing
            // topPlayersHistory is an array of { timestamp: ..., scores: { player1: score, player2: score } }
            // We need to extract the history for a single player first.
            const playerSpecificHistory = topPlayersHistory
                .filter(entry => entry.scores.hasOwnProperty(playerName))
                .map(entry => ({
                    timestamp: entry.timestamp,
                    score: entry.scores[playerName]
                }))
                .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

            playerSpecificHistory.forEach((entry, index) => {
                const currentTimestamp = new Date(entry.timestamp);
                const currentScore = entry.score;

                // Handle initial point (0 score)
                if (index === 0 && currentScore === 0) {
                    interpolatedPlayerHistory[playerName].push({
                        x: currentTimestamp.toISOString(),
                        y: 0
                    });
                    previousScore = 0;
                    previousTimestamp = currentTimestamp;
                    return;
                }

                // If this is the first actual score point (not the initial 0)
                if (previousTimestamp === null) {
                    // Add an initial 0 score point slightly before the first actual score
                    const initialZeroTimestamp = new Date(currentTimestamp.getTime() - 1); // 1ms before
                    interpolatedPlayerHistory[playerName].push({
                        x: initialZeroTimestamp.toISOString(),
                        y: 0
                    });
                    previousScore = 0;
                    previousTimestamp = initialZeroTimestamp;
                }

                // Interpolate if there's a score increase
                if (currentScore > previousScore) {
                    const startInterpolationTime = new Date(Math.max(previousTimestamp.getTime(), currentTimestamp.getTime() - interpolationDurationMs));
                    
                    for (let i = 1; i <= interpolationSteps; i++) {
                        const interpTime = new Date(startInterpolationTime.getTime() + (currentTimestamp.getTime() - startInterpolationTime.getTime()) / interpolationSteps * i);
                        const interpScore = previousScore + (currentScore - previousScore) / interpolationSteps * i;
                        interpolatedPlayerHistory[playerName].push({
                            x: interpTime.toISOString(),
                            y: Math.round(interpScore)
                        });
                    }
                } else if (currentScore < previousScore) {
                    // If score decreases (e.g., admin adjustment), just jump to new score
                    interpolatedPlayerHistory[playerName].push({
                        x: currentTimestamp.toISOString(),
                        y: currentScore
                    });
                }
                
                // Add the actual current score point
                interpolatedPlayerHistory[playerName].push({
                    x: currentTimestamp.toISOString(),
                    y: currentScore
                });

                previousScore = currentScore;
                previousTimestamp = currentTimestamp;
            });
        });

        // Prepare datasets for Chart.js using interpolated data
        const datasets = playerNames.map((playerName, index) => {
            const colors = [
                'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 206, 86)', 
                'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)',
                'rgb(199, 199, 199)', 'rgb(83, 102, 255)', 'rgb(40, 159, 64)',
                'rgb(210, 99, 132)'
            ];
            const color = colors[index % colors.length];

            return {
                label: playerName,
                data: interpolatedPlayerHistory[playerName],
                borderColor: color,
                backgroundColor: color,
                fill: false,
                tension: 0.1 // Keep a slight tension for overall smoothness
            };
        });

        // Collect all unique timestamps from interpolated data for labels
        // Chart.js time scale handles x-values directly, so labels array is less critical here
        // but we can use it to define the overall range if needed.
        // For now, let's just ensure the data points have x values.
        const labels = []; // Labels are not strictly needed for time scale with x/y data points

        new Chart(ctx, {
            type: 'line',
            data: {
                // labels: labels, // Not strictly needed for time scale with x/y data points
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Top Players Score Over Time'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            title: function(context) {
                                // Display formatted date as title
                                return new Date(context[0].parsed.x).toLocaleString();
                            },
                            label: function(context) {
                                // Display player name and score
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y;
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time', // Use time scale
                        time: {
                            unit: 'hour', // Adjust unit as needed (e.g., 'day', 'hour')
                            tooltipFormat: 'MMM D, YYYY, h:mm:ss a',
                            displayFormats: {
                                hour: 'MMM D, h:mm a',
                                day: 'MMM D'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        },
                        ticks: {
                            display: false // Hide X-axis labels
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Score'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function populatePlayerRankings(allPlayersRanked) {
        const tableBody = document.querySelector('#playerRankings tbody');
        tableBody.innerHTML = ''; // Clear existing rows

        if (!allPlayersRanked || allPlayersRanked.length === 0) {
            const row = tableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 3;
            cell.textContent = 'No players to display.';
            cell.className = 'px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500';
            return;
        }

        allPlayersRanked.forEach((player, index) => {
            const row = tableBody.insertRow();
            row.className = (index % 2 === 0) ? 'bg-white' : 'bg-gray-50';

            const rankCell = row.insertCell();
            rankCell.className = 'px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900';
            rankCell.textContent = index + 1; // Rank starts from 1

            const usernameCell = row.insertCell();
            usernameCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
            usernameCell.textContent = player.username;

            const scoreCell = row.insertCell();
            scoreCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
            scoreCell.textContent = player.score;
        });
    }
});