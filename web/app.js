async function fetchDashboardData() {
    // 1. EC2에서 실시간 비트코인 데이터 받아오기
    const btcRes = await fetch('http://ec2-server:port/bitcoin');
    const btcData = await btcRes.json();

    // 2. 받아온 비트코인 데이터를 모델 input으로 predict API에 전달
    const predRes = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: btcData.input })
    });
    const predData = await predRes.json();

    // 3. Lambda에서 모델 최신 학습일 받아오기
    const lambdaRes = await fetch('http://lambda-api-endpoint/latest-trained');
    const lambdaData = await lambdaRes.json();

    // 4. 대시보드에 데이터 표시
    document.getElementById('btc-price').innerText = btcData.price;
    document.getElementById('prediction').innerText =
        predData.prediction && predData.prediction.result
            ? JSON.stringify(predData.prediction.result)
            : '-';
    document.getElementById('last-trained').innerText = lambdaData.last_trained;
}

// 1분(60,000ms)마다 데이터 갱신
setInterval(fetchDashboardData, 60000);
fetchDashboardData(); // 최초 1회 실행