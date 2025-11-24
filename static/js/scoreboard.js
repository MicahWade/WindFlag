document.addEventListener('DOMContentLoaded', function() {
    let scoreboardChart; // Declare chart globally so it can be updated
    let allPlayersRanked = []; // Store the current state of ranked players
    
    // Always fetch initial scoreboard data
    fetch('/api/scoreboard_data')
        .then(response => response.json())
        .then(data => {
            if (ENABLE_LIVE_SCORE_GRAPH) { // Only render graph if enabled
                renderScoreboardGraph(data.top_players_history, data.graph_type);
            }
            populatePlayerRankings(data.all_players_ranked);
            allPlayersRanked = data.all_players_ranked; // Initialize the ranked players data
        })
        .catch(error => console.error('Error fetching scoreboard data:', error));

    // Only connect to WebSocket and listen for live updates if ENABLE_LIVE_SCORE_GRAPH is true
    if (ENABLE_LIVE_SCORE_GRAPH) {
        // Connect to the Socket.IO server
        const socket = io(); // Connects to the current host
        
        // Listen for score_update events from the server
        socket.on('score_update', function(data) {
            console.log('Score update received:', data);
            
            const username = data.username;
            const newScore = data.score;
            const timestamp = new Date().toISOString(); // Use current time for the new point

            // Update the global user score display in the header
            const userScoreDisplay = document.getElementById('userScoreDisplay');
            if (userScoreDisplay && data.user_id == current_user_id) { // Assuming current_user_id is available in JS
                userScoreDisplay.textContent = newScore;
            }

            // Update the chart data
            if (scoreboardChart) {
                let playerDataset = scoreboardChart.data.datasets.find(ds => ds.label === username);

                if (playerDataset) {
                    // Add new point to existing dataset
                    playerDataset.data.push({ x: timestamp, y: newScore });
                } else {
                    // If this is a new player on the scoreboard or a player not yet charted
                    // We'll need to re-fetch full scoreboard data to properly add them with history
                    // For simplicity, for now, we'll just add a single point
                    // A more robust solution would re-fetch the entire `top_players_history`
                    const computedStyle = getComputedStyle(document.body);
                    const colors = [];
                    for (let i = 1; i <= 10; i++) {
                        const color = computedStyle.getPropertyValue(`--chart-color-${i}`).trim();
                        if (color) colors.push(color);
                    }
                    const newPlayerColor = colors[scoreboardChart.data.datasets.length % colors.length];

                    scoreboardChart.data.datasets.push({
                        label: username,
                        data: [{ x: timestamp, y: newScore }],
                        borderColor: newPlayerColor,
                        backgroundColor: scoreboardChart.options.plugins.legend.labels.usePointStyle ? newPlayerColor : newPlayerColor.replace('rgb(', 'rgba(').replace(')', `, 0.25)`),
                        fill: scoreboardChart.data.datasets[0]?.fill || false, // Match fill style of others
                        tension: 0.1,
                        spanGaps: true
                    });
                }
                scoreboardChart.update(); // Redraw the chart
            }

            // Update the ranked players table
            // This is a simplified update. For accurate rankings, we should re-fetch all_players_ranked
            // or re-sort the existing array. For a quick live update, we'll adjust the score
            // and re-sort a local copy, then repopulate.
            let playerIndex = allPlayersRanked.findIndex(p => p.username === username);
            if (playerIndex !== -1) {
                allPlayersRanked[playerIndex].score = newScore;
            } else {
                // Add new player to the list (simple, might need more data from server for proper entry)
                allPlayersRanked.push({ username: username, score: newScore });
            }
            // Sort by score descending and then populate
            allPlayersRanked.sort((a, b) => b.score - a.score);
            populatePlayerRankings(allPlayersRanked);
        });
    }

    function renderScoreboardGraph(topPlayersHistory, graphType) {
        const ctx = document.getElementById('scoreboardChart').getContext('2d');
        
        // Get computed chart colors from CSS variables
        const computedStyle = getComputedStyle(document.body);
        const colors = [];
        for (let i = 1; i <= 10; i++) {
            const color = computedStyle.getPropertyValue(`--chart-color-${i}`).trim();
            if (color) colors.push(color);
        }
        // Fallback colors if CSS variables are not defined
        if (colors.length === 0) {
            colors.push(
                'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 206, 86)', 
                'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)',
                'rgb(199, 199, 199)', 'rgb(83, 102, 255)', 'rgb(40, 159, 64)',
                'rgb(210, 99, 132)'
            );
        }
        
        if (!topPlayersHistory || Object.keys(topPlayersHistory).length === 0) {
            ctx.font = '18px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No data available for graph.', ctx.canvas.width / 2, ctx.canvas.height / 2);
            return;
        }
        
        // Extract unique player names from the new structure
        const playerNames = Object.keys(topPlayersHistory);
        
        // Prepare datasets for Chart.js
        const datasets = playerNames.map((playerName, index) => {
            const color = colors[index % colors.length];
            
            return {
                label: playerName,
                data: topPlayersHistory[playerName], // Directly use the player's history
                borderColor: color,
                backgroundColor: graphType === 'area' ? color.replace('rgb(', 'rgba(').replace(')', `, 0.25)`) : color, // Set transparent background for area graph
                fill: graphType === 'area', // Set fill based on graphType
                tension: 0.1, // Smooth curves for better visual
                spanGaps: true // Connect points across null or undefined data
            };
        });

        // Destroy existing chart if it exists
        if (scoreboardChart) {
            scoreboardChart.destroy();
        }

        scoreboardChart = new Chart(ctx, {
            type: 'line', // Chart.js uses 'line' type for both line and area graphs, 'fill' property differentiates
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index', // Changed to 'index' for better multi-dataset tooltips
                    intersect: false, // Allow tooltip to activate when near a data point
                },
                plugins: {
                    title: {
                        display: false, // Remove the chart title
                    },
                    legend: {
                        display: true, // Display legend to show player names and colors
                        position: 'top',
                        labels: {
                            color: computedStyle.getPropertyValue('--text-color-primary').trim(), // Use theme text color
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            filter: function(tooltipItem) {
                                // Only show tooltip items if the y-value is not null/undefined AND the dataset index is valid
                                return tooltipItem.parsed.y !== null && tooltipItem.parsed.y !== undefined && tooltipItem.datasetIndex !== undefined;
                            },
                            title: function(context) {
                                if (!context || context.length === 0 || !context[0].parsed || context[0].parsed.y === null || context[0].parsed.y === undefined) {
                                    return '';
                                }
                                if (context[0].parsed.x) {
                                    const date = new Date(context[0].parsed.x);
                                    // Use toLocaleString for flexible date/time formatting
                                    return date.toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true });
                                }
                                return '';
                            },
                            label: function(context) {
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
                            tooltipFormat: 'MMM d, yyyy, h:mm a', // Display both date and time in tooltip
                            displayFormats: {
                                hour: 'MMM d, h:mm a',
                                day: 'MMM d'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time',
                            color: computedStyle.getPropertyValue('--text-color-primary').trim(),
                        },
                        ticks: {
                            color: computedStyle.getPropertyValue('--text-color-secondary').trim(),
                        },
                        grid: {
                            color: computedStyle.getPropertyValue('--chart-grid-color').trim(),
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Score',
                            color: computedStyle.getPropertyValue('--text-color-primary').trim(),
                        },
                        beginAtZero: true,
                        ticks: {
                            color: computedStyle.getPropertyValue('--text-color-secondary').trim(),
                        },
                        grid: {
                            color: computedStyle.getPropertyValue('--chart-grid-color').trim(),
                        }
                    }
                }
            }
        });
    }

    function populatePlayerRankings(players) {
        const tableBody = document.querySelector('#playerRankings tbody');
        tableBody.innerHTML = ''; // Clear existing rows

        if (!players || players.length === 0) {
            const row = tableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 3;
            cell.textContent = 'No players to display.';
            cell.className = 'px-6 py-4 whitespace-nowrap text-center text-sm theme-no-data-text';
            return;
        }

        players.forEach((player, index) => {
            const row = tableBody.insertRow();
            row.className = (index % 2 === 0) ? 'theme-table-row-even' : 'theme-table-row-odd';

            const rankCell = row.insertCell();
            rankCell.className = 'px-6 py-4 whitespace-nowrap text-sm font-medium theme-table-body-cell';
            rankCell.textContent = index + 1; // Rank starts from 1

            const usernameCell = row.insertCell();
            usernameCell.className = 'px-6 py-4 whitespace-nowrap text-sm theme-table-body-cell';
            const userLink = document.createElement('a');
            userLink.href = `/profile/${player.username}`;
            userLink.textContent = player.username;
            userLink.className = 'theme-link';
            usernameCell.appendChild(userLink);

            const scoreCell = row.insertCell();
            scoreCell.className = 'px-6 py-4 whitespace-nowrap text-sm theme-table-body-cell';
            scoreCell.textContent = player.score;
        });
    }
});