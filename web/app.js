let priceChart = null;

function createChart(labels, prices) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (priceChart) {
        priceChart.destroy();
    }

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'BTC/USDT',
                data: prices,
                borderColor: '#00b894',
                backgroundColor: 'rgba(0, 184, 148, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `$${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

async function fetchDashboardData() {
    try {
        // 1. 실시간 비트코인 데이터 받아오기 (로컬 서버에서)
        const btcRes = await fetch('/api/bitcoin');
        const btcData = await btcRes.json();

        // 2. 받아온 비트코인 데이터를 모델 input으로 predict API에 전달
        const predRes = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: btcData.input })
        });
        const predData = await predRes.json();

        // 3. 모델 최신 학습일 받아오기 (로컬 서버에서)
        const modelRes = await fetch('/api/model-info');
        const modelData = await modelRes.json();

        // 4. 대시보드에 데이터 표시
        document.getElementById('btc-price').innerText = btcData.price;
        document.getElementById('prediction').innerText =
            predData.prediction && predData.prediction.result
                ? JSON.stringify(predData.prediction.result)
                : '-';
        document.getElementById('last-trained').innerText = modelData.last_trained || '모델이 로드되지 않음';

        // 5. 차트 데이터 업데이트
        if (btcData.chart_data) {
            const labels = btcData.chart_data.timestamps.map(timestamp => 
                new Date(timestamp).toLocaleTimeString()
            );
            const prices = btcData.chart_data.prices;
            createChart(labels, prices);
        }
    } catch (error) {
        console.error('데이터를 가져오는 중 오류 발생:', error);
        // 에러 발생 시 UI에 표시
        document.getElementById('btc-price').innerText = '데이터 로드 실패';
        document.getElementById('prediction').innerText = '예측 불가';
        document.getElementById('last-trained').innerText = '정보 없음';
    }
}

// 1분(60,000ms)마다 데이터 갱신
setInterval(fetchDashboardData, 60000);
fetchDashboardData(); // 최초 1회 실행