document.addEventListener('DOMContentLoaded', function() {
    let scoreboardChart; // Declare chart globally so it can be updated
    let allPlayersRanked = []; // Store the current state of ranked players
    
    // Always fetch initial scoreboard data
    fetch('/api/scoreboard_data')
        .then(response => response.json())
        .then(data => {
            // Live score graph functionality is removed, so always try to render if data is available
            renderScoreboardGraph(data.top_players_history, data.graph_type);
            populatePlayerRankings(data.all_players_ranked);
            allPlayersRanked = data.all_players_ranked; // Initialize the ranked players data
        })
        .catch(error => console.error('Error fetching scoreboard data:', error));

    // Socket.IO integration removed. Live updates will no longer be handled client-side via websockets.

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
                        display: false, // Do not display legend for users
                    },
                    tooltip: {
                        mode: 'nearest', // Changed mode to 'nearest' as requested
                        intersect: false, // Allows selecting points when hovering near the line
                        callbacks: {
                            title: function(context) {
                                return ''; // Do not display time
                            },
                            label: function(context) {
                                let label = context.dataset.label; // Get the user's label
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
                            display: false, // Do not display X-axis title (Time)
                        },
                        ticks: {
                            display: false, // Do not display X-axis ticks/labels
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
            usernameCell.appendChild(userLink);

            const scoreCell = row.insertCell();
            scoreCell.className = 'px-6 py-4 whitespace-nowrap text-sm theme-table-body-cell';
            scoreCell.textContent = player.score;
        });

        if ($.fn.DataTable.isDataTable('#playerRankings')) {
            $('#playerRankings').DataTable().destroy();
        }
        $('#playerRankings').DataTable();
    }
});