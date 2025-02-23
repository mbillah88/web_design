function calculateTotal() {
    // Get table rows
    var table = document.getElementById("purchaseOrderTable");
    var rows = table.getElementsByTagName("tr");

    // Loop through rows and calculate totals
    for (var i = 1; i < rows.length; i++) {
        var quantityCell = rows[i].cells[2];
        var priceCell = rows[i].cells[3];
        var totalCell = rows[i].cells[4];

        var quantity = parseFloat(quantityCell.textContent);
        var price = parseFloat(priceCell.textContent);
        var total = quantity * price;

        totalCell.textContent = total.toFixed(2);
    }
}