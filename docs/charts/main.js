// Public Good Index - D3 chart rendering
// Charts load processed JSON data and render visualizations

async function loadData(path) {
    try {
        const response = await fetch(path);
        return await response.json();
    } catch (e) {
        console.log(`Data not yet available: ${path}`);
        return null;
    }
}

async function init() {
    const placeholder = document.getElementById("charts-placeholder");

    const taxData = await loadData("data/tax_burden.json");
    const spendingData = await loadData("data/spending_breakdown.json");
    const scoreData = await loadData("data/public_good_scores.json");

    if (!taxData && !spendingData && !scoreData) {
        placeholder.textContent = "No data available yet. Run the notebooks to generate chart data.";
        return;
    }

    placeholder.style.display = "none";

    if (taxData) renderTaxBurdenChart(taxData);
    if (spendingData) renderInvestmentCostChart(spendingData);
    if (scoreData) renderPublicGoodChart(scoreData);
}

function renderTaxBurdenChart(data) {
    // TODO: horizontal bar chart of tax burden % by state
}

function renderInvestmentCostChart(data) {
    // TODO: stacked bar chart showing investment vs cost ratio per state
}

function renderPublicGoodChart(data) {
    // TODO: ranked bar chart or US choropleth of public good scores
}

init();
