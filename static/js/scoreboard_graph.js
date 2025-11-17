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
                data: topPlayersHistory.map(entry => entry.scores[playerName] || 0), // Use 0 if player didn't exist at that time
                borderColor: color,
                backgroundColor: color,
                fill: false,
                tension: 0.1
            };
        });

        // Prepare labels (timestamps) - use raw ISO strings for time scale
        const labels = topPlayersHistory.map(entry => entry.timestamp);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
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
                                return new Date(context[0].label).toLocaleString();
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
