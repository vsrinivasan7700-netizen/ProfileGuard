function crateRiskChart(riskData) {

    const canvas = document.getElementById("riskChart");

    if (!canvas) {
        return;
    }

    new Chart(canvas, {

        type: "doughnut",

        data: {

            labels: [
                "Low Risk",
                "Medium Risk",
                "High Risk"
            ],

            datasets: [{

                data: [
                    riskData.low,
                    riskData.medium,
                    riskData.high
                ],

                backgroundColor: [
                    "#22c55e",
                    "#f59e0b",
                    "#ef4444"
                ],

                borderWidth: 0

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    position: "bottom",
                    labels: {
                        color: "#cbd5e1",
                        padding: 20
                    }
                }

            }

        }

    });

}