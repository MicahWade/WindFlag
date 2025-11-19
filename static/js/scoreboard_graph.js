document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/scoreboard_data')
        .then(response => response.json())
        .then(data => {
            renderScoreboardGraph(data.top_players_history, data.graph_type);
            populatePlayerRankings(data.all_players_ranked);
        })
        .catch(error => console.error('Error fetching scoreboard data:', error));

    function renderScoreboardGraph(topPlayersHistory, graphType) {
        const ctx = document.getElementById('scoreboardChart').getContext('2d');

        // Helper function to convert RGB to RGBA
        function rgbToRgba(rgb, alpha) {
            const parts = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
            if (parts) {
                return `rgba(${parts[1]}, ${parts[2]}, ${parts[3]}, ${alpha})`;
            }
            return rgb; // Return original if format doesn't match
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
            // Assign a color to each player (you might want a more sophisticated color palette)
            const colors = [
                'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 206, 86)', 
                'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)',
                'rgb(199, 199, 199)', 'rgb(83, 102, 255)', 'rgb(40, 159, 64)',
                'rgb(210, 99, 132)'
            ];
            const color = colors[index % colors.length];

            return {
                label: playerName,
                data: topPlayersHistory[playerName], // Directly use the player's history
                borderColor: color,
                backgroundColor: graphType === 'area' ? rgbToRgba(color, 0.25) : color, // Set transparent background for area graph
                fill: graphType === 'area', // Set fill based on graphType
                tension: 0, // Render straight lines
                spanGaps: true // Connect points across null or undefined data
            };
        });

        new Chart(ctx, {
            type: 'line', // Chart.js uses 'line' type for both line and area graphs, 'fill' property differentiates
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'nearest',
                    intersect: false, // Allow tooltip to activate when near a data point
                    hitRadius: 20 // Increased hit radius for tooltip activation
                },
                plugins: {
                    title: {
                        display: false, // Remove the chart title
                    },
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        // ... existing tooltip configuration ...
                        callbacks: {
                            filter: function(tooltipItem) {
                                // Only show tooltip items if the y-value is not null/undefined AND the dataset index is valid
                                return tooltipItem.parsed.y !== null && tooltipItem.parsed.y !== undefined && tooltipItem.datasetIndex !== undefined;
                            },
                            title: function(context) {
                                // If there are no valid data points, return an empty string to hide the title
                                if (!context || context.length === 0 || !context[0].parsed || context[0].parsed.y === null || context[0].parsed.y === undefined) {
                                    return '';
                                }
                                // Explicitly format the date to ensure Month Day, Year
                                if (context[0].parsed.x) {
                                    const date = new Date(context[0].parsed.x);
                                    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
                                }
                                return '';
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
                            tooltipFormat: 'MMM d, YYYY', // Display only date, no time
                            displayFormats: {
                                hour: 'MMM d, h:mm a',
                                day: 'MMM d'
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
            cell.className = 'px-6 py-4 whitespace-nowrap text-center text-sm text-gray-400';
            return;
        }

        allPlayersRanked.forEach((player, index) => {
            const row = tableBody.insertRow();
            row.className = (index % 2 === 0) ? 'bg-gray-800 border-b border-gray-700' : 'bg-gray-700 border-b border-gray-700';

            const rankCell = row.insertCell();
            rankCell.className = 'px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-200';
            rankCell.textContent = index + 1; // Rank starts from 1

            const usernameCell = row.insertCell();
            usernameCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-300';
            // Create an anchor tag
            const userLink = document.createElement('a');
            userLink.href = `/profile/${player.username}`; // Construct the URL
            userLink.textContent = player.username;
            userLink.className = 'text-blue-400 hover:text-blue-300'; // Add some styling for links
            usernameCell.appendChild(userLink); // Append the link to the cell

            const scoreCell = row.insertCell();
            scoreCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-300';
            scoreCell.textContent = player.score;
        });
    }
});
