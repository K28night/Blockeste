// Handle form submission
document.getElementById('propertyCostForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Get property cost in ETH
    const propertyCostETH = parseFloat(document.getElementById('propertyCostETH').value);

    // Get selected currency
    const currency = document.getElementById('currency').value;

    // Validate input
    if (isNaN(propertyCostETH)) {
        alert('Please enter a valid property cost in ETH.');
        return;
    }

    // Constants for calculations
    const securityTransactionReductionRate = 0.01; // 1%
    const brokerageRate = 0.02; // 2%

    // ETH conversion rates (example values)
    const ethToInr = 200000; // 1 ETH = 200,000 INR
    const ethToUsd = 2500; // 1 ETH = 2,500 USD
    const ethToEur = 2200; // 1 ETH = 2,200 EUR

    // Calculate security transaction reduction
    const securityTransactionReduction = propertyCostETH * securityTransactionReductionRate;

    // Calculate brokerage
    const brokerage = propertyCostETH * brokerageRate;

    // Calculate final amount in ETH
    const finalAmountETH = propertyCostETH - securityTransactionReduction - brokerage;

    // Convert final amount to selected currency
    let finalAmount;
    switch (currency) {
        case 'INR':
            finalAmount = finalAmountETH * ethToInr;
            break;
        case 'USD':
            finalAmount = finalAmountETH * ethToUsd;
            break;
        case 'EUR':
            finalAmount = finalAmountETH * ethToEur;
            break;
        default:
            finalAmount = finalAmountETH; // Default to ETH
    }

    // Display results
    document.getElementById('securityTransactionReduction').textContent = `${securityTransactionReduction.toFixed(2)} ETH`;
    document.getElementById('brokerageAmount').textContent = `${brokerage.toFixed(2)} ETH`;
    document.getElementById('finalAmount').textContent = `${finalAmount.toFixed(2)} ${currency}`;
});