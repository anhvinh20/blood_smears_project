/* static/js/detail-results.js */

// JavaScript for the detail results page

document.addEventListener('DOMContentLoaded', function() {
    // Load data from sessionStorage
    const detailData = JSON.parse(sessionStorage.getItem('detailResults') || '{}');
    
    // Create chart if data exists
    if (detailData.chartData) {
        createComparisonChart(detailData.chartData);
    }
    
    // Display FP and FN images
    if (detailData.fpImage) {
        document.getElementById('fpImage').src = 'data:image/jpeg;base64,' + detailData.fpImage;
        document.getElementById('fpCount').innerHTML = `<strong>Tổng số FP: ${detailData.fpCount || 0}</strong>`;
    }
    
    if (detailData.fnImage) {
        document.getElementById('fnImage').src = 'data:image/jpeg;base64,' + detailData.fnImage;
        document.getElementById('fnCount').innerHTML = `<strong>Tổng số FN: ${detailData.fnCount || 0}</strong>`;
    }
    
    // Display statistics
    if (detailData.statistics) {
        displayStatistics(detailData.statistics);
    }
});

// Create the comparison chart
function createComparisonChart(chartData) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Detection',
                    data: chartData.detection,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Ground Truth',
                    data: chartData.groundTruth,
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'So sánh số lượng tế bào theo loại'
                }
            }
        }
    });
}

// Display statistics
function displayStatistics(statistics) {
    let statsHTML = '';
    
    Object.entries(statistics).forEach(([key, value]) => {
        statsHTML += `
            <div class="col-md-3 mb-3">
                <div class="card">
                    <div class="card-body text-center">
                        <h6>${key}</h6>
                        <h4 class="text-primary">${value}</h4>
                    </div>
                </div>
            </div>
        `;
    });
    
    document.getElementById('detailStats').innerHTML = statsHTML;
}