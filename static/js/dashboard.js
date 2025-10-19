// Converge Dashboard JavaScript

// 通用工具函數
function formatNumber(num) {
    return num.toLocaleString('zh-TW');
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('zh-TW');
}

// 健康檢查
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        const indicator = document.getElementById('status-indicator');
        if (indicator) {
            if (data.status === 'healthy') {
                indicator.innerHTML = '<i class="bi bi-circle-fill text-success"></i> 運作中';
            } else {
                indicator.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> 異常';
            }
        }

    } catch (error) {
        const indicator = document.getElementById('status-indicator');
        if (indicator) {
            indicator.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> 離線';
        }
    }
}

// 定期檢查健康狀態
setInterval(checkHealth, 60000); // 每分鐘檢查一次

// 頁面載入時檢查
document.addEventListener('DOMContentLoaded', function() {
    checkHealth();
    console.log('🤖 Converge Dashboard 已載入');
});
