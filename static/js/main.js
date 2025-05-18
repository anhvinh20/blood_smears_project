/* static/js/main.js */

// Main JavaScript file for Blood Smears application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form handling
    initFormHandling();
    
    // Initialize global event listeners
    window.resetForm = resetForm;
    window.showDetailResults = showDetailResults;
});

// Global variables
let analysisData = null;

// Form handling initialization
function initFormHandling() {
    const imageInput = document.getElementById('imageInput');
    const labelInput = document.getElementById('labelInput');
    const imagePreview = document.getElementById('imagePreview');
    const labelPreview = document.getElementById('labelPreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const uploadForm = document.getElementById('uploadForm');
    const loading = document.getElementById('loading');
    
    // Handle image file selection
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" class="img-fluid" alt="Preview">`;
                analyzeBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle label file selection
    labelInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            labelPreview.innerHTML = `
                <div class="alert alert-info m-3">
                    <i class="bi bi-file-text"></i> ${file.name}
                    <br><small>Ground Truth file đã được chọn</small>
                </div>
            `;
        } else {
            labelPreview.innerHTML = '<p class="text-center text-muted py-5">Chưa có file label được chọn</p>';
        }
    });

    // Handle form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const imageFile = imageInput.files[0];
        const labelFile = labelInput.files[0];
        
        if (!imageFile) {
            alert('Vui lòng chọn file ảnh');
            return;
        }

        const formData = new FormData();
        formData.append('image', imageFile);
        if (labelFile) {
            formData.append('label', labelFile);
        }

        // Hide previous results and show loading
        hideResults();
        loading.style.display = 'block';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                displayResults(data);
            } else {
                alert('Lỗi: ' + (data.error || 'Có lỗi xảy ra'));
            }
        } catch (error) {
            alert('Lỗi kết nối: ' + error.message);
        } finally {
            loading.style.display = 'none';
        }
    });
}

// Display analysis results
function displayResults(data) {
    // Store data globally for detail page
    analysisData = data;
    window.analysisData = data;
    
    // Display Stage 1 results
    displayStage1Results(data);
    
    // Show divider
    document.getElementById('stageDivider').style.display = 'block';
    
    // Display Stage 2 results
    displayStage2Results(data);
}

// Display Stage 1 results (Healthy/Unhealthy)
function displayStage1Results(data) {
    document.getElementById('stage1Total').textContent = data.stage1.total;
    document.getElementById('stage1Healthy').textContent = data.stage1.num_healthy;
    document.getElementById('stage1Unhealthy').textContent = data.stage1.num_unhealthy;
    document.getElementById('stage1Image').src = 'data:image/jpeg;base64,' + data.stage1.image;
    document.getElementById('stage1Results').style.display = 'block';
}

// Display Stage 2 results (Detailed classification)
function displayStage2Results(data) {
    document.getElementById('totalCells').textContent = data.stage2.total_cells;
    
    // Cell type colors
    const cellColors = {
        'TJ': 'text-info',
        'TA': 'text-secondary',
        'S': 'text-warning',
        'G': 'text-danger',
        'Healthy': 'text-success',
        'Others': 'text-dark',
        'Diff': 'text-primary'
    };
    
    // Display cell counts table
    createCellCountsTable(data.stage2.cell_counts, data.stage2.total_cells, cellColors);
    
    // Display result image
    document.getElementById('resultImage').src = 'data:image/jpeg;base64,' + data.stage2.image;
    
    // Handle ground truth if available
    const hasGT = data.ground_truth != null;
    
    if (hasGT) {
        displayGroundTruth(data, cellColors);
    } else {
        centerDetectionElements();
    }
    
    // Show stage 2 results
    document.getElementById('stage2Results').style.display = 'block';
}

// Create cell counts table
function createCellCountsTable(cellCounts, totalCells, cellColors) {
    let tableHTML = '<table class="table table-hover">';
    tableHTML += '<thead><tr><th>Loại tế bào</th><th>Số lượng</th><th>Tỷ lệ</th></tr></thead><tbody>';
    
    for (const [cellType, count] of Object.entries(cellCounts)) {
        const percentage = totalCells > 0 ? 
            ((count / totalCells) * 100).toFixed(1) : 0;
        const colorClass = cellColors[cellType] || 'text-secondary';
        tableHTML += `<tr>
            <td><i class="bi bi-circle-fill ${colorClass}"></i> ${cellType}</td>
            <td>${count}</td>
            <td>${percentage}%</td>
        </tr>`;
    }
    
    tableHTML += '</tbody></table>';
    document.getElementById('cellCountsTable').innerHTML = tableHTML;
}

// Display ground truth data
function displayGroundTruth(data, cellColors) {
    // Show ground truth elements
    document.getElementById('gtTotalCard').style.display = 'block';
    document.getElementById('gtCountsCard').style.display = 'block';
    document.getElementById('gtImageCard').style.display = 'block';
    document.getElementById('metricsCard').style.display = 'block';
    document.getElementById('detailBtn').style.display = 'inline-block';
    
    // Reset layout classes
    document.getElementById('detectionTotalCard').classList.remove('mx-auto');
    document.getElementById('detectionCountsCol').classList.remove('mx-auto');
    document.getElementById('detectionImageCol').classList.remove('mx-auto');
    
    // Display GT data
    document.getElementById('gtTotalCells').textContent = data.ground_truth.total;
    
    // GT counts table
    let gtTableHTML = '<table class="table table-hover">';
    gtTableHTML += '<thead><tr><th>Loại tế bào</th><th>Số lượng</th><th>Tỷ lệ</th></tr></thead><tbody>';
    
    for (const [cellType, count] of Object.entries(data.ground_truth.counts)) {
        const percentage = data.ground_truth.total > 0 ? 
            ((count / data.ground_truth.total) * 100).toFixed(1) : 0;
        const colorClass = cellColors[cellType] || 'text-secondary';
        gtTableHTML += `<tr>
            <td><i class="bi bi-circle-fill ${colorClass}"></i> ${cellType}</td>
            <td>${count}</td>
            <td>${percentage}%</td>
        </tr>`;
    }
    
    gtTableHTML += '</tbody></table>';
    document.getElementById('gtCountsTable').innerHTML = gtTableHTML;
    
    // GT image
    document.getElementById('gtImage').src = 'data:image/jpeg;base64,' + data.ground_truth.image;
    
    // Metrics
    if (data.comparison) {
        displayMetrics(data.comparison);
    }
}

// Display metrics
function displayMetrics(comparison) {
    let metricsHTML = `
        <div class="metrics-item">
            <strong>Precision:</strong> 
            <span class="badge bg-info">${(comparison.precision * 100).toFixed(1)}%</span>
        </div>
        <div class="metrics-item">
            <strong>Recall:</strong> 
            <span class="badge bg-info">${(comparison.recall * 100).toFixed(1)}%</span>
        </div>
        <div class="metrics-item">
            <strong>F1 Score:</strong> 
            <span class="badge bg-info">${(comparison.f1 * 100).toFixed(1)}%</span>
        </div>
        <div class="metrics-item">
            <strong>True Positives:</strong> 
            <span class="badge bg-success">${comparison.tp}</span>
        </div>
        <div class="metrics-item">
            <strong>False Positives:</strong> 
            <span class="badge bg-warning">${comparison.fp}</span>
        </div>
        <div class="metrics-item">
            <strong>False Negatives:</strong> 
            <span class="badge bg-danger">${comparison.fn}</span>
        </div>
    `;
    document.getElementById('metricsContent').innerHTML = metricsHTML;
}

// Center detection elements when no ground truth
function centerDetectionElements() {
    // Hide ground truth elements
    document.getElementById('gtTotalCard').style.display = 'none';
    document.getElementById('gtCountsCard').style.display = 'none';
    document.getElementById('gtImageCard').style.display = 'none';
    document.getElementById('metricsCard').style.display = 'none';
    document.getElementById('detailBtn').style.display = 'none';
    
    // Add centering classes
    document.getElementById('detectionTotalCard').classList.add('mx-auto');
    document.getElementById('detectionCountsCol').classList.add('mx-auto');
    document.getElementById('detectionImageCol').classList.add('mx-auto');
}

// Hide all results
function hideResults() {
    document.getElementById('stage1Results').style.display = 'none';
    document.getElementById('stage2Results').style.display = 'none';
    document.getElementById('stageDivider').style.display = 'none';
}

// Reset form and results
function resetForm() {
    // Reset form inputs
    document.getElementById('imageInput').value = '';
    document.getElementById('labelInput').value = '';
    document.getElementById('imagePreview').innerHTML = '<p class="text-center text-muted py-5">Ảnh xem trước sẽ hiển thị ở đây</p>';
    document.getElementById('labelPreview').innerHTML = '<p class="text-center text-muted py-5">Chưa có file label được chọn</p>';
    
    // Hide results
    hideResults();
    
    // Disable analyze button
    document.getElementById('analyzeBtn').disabled = true;
    
    // Reset data
    analysisData = null;
    window.analysisData = null;
}

// Navigate to detail results page
function showDetailResults() {
    if (window.analysisData && window.analysisData.ground_truth) {
        // Prepare data for detail page
        const detailData = {
            chartData: window.analysisData.chart_data,
            fpImage: window.analysisData.fp_image,
            fnImage: window.analysisData.fn_image,
            fpCount: window.analysisData.fp_count,
            fnCount: window.analysisData.fn_count,
            statistics: {
                'Total Detection': window.analysisData.stage2.total_cells,
                'Total Ground Truth': window.analysisData.ground_truth.total,
                'Precision': window.analysisData.comparison ? 
                    (window.analysisData.comparison.precision * 100).toFixed(1) + '%' : 'N/A',
                'Recall': window.analysisData.comparison ? 
                    (window.analysisData.comparison.recall * 100).toFixed(1) + '%' : 'N/A',
                'F1 Score': window.analysisData.comparison ? 
                    (window.analysisData.comparison.f1 * 100).toFixed(1) + '%' : 'N/A',
                'True Positives': window.analysisData.comparison ? 
                    window.analysisData.comparison.tp : 'N/A',
                'False Positives': window.analysisData.comparison ? 
                    window.analysisData.comparison.fp : 'N/A',
                'False Negatives': window.analysisData.comparison ? 
                    window.analysisData.comparison.fn : 'N/A'
            }
        };
        
        // Store in sessionStorage
        sessionStorage.setItem('detailResults', JSON.stringify(detailData));
        
        // Navigate to detail page
        window.location.href = '/detail-results';
    }
}