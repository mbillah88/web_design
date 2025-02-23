
//Enter Input Button Next Filed element...
function moveToNextField(event, nextFieldID) {
  if (event.key === "Enter") {
    document.getElementById(nextFieldID).focus();
    event.preventDefault();
  }
}
/*
function moveToNextField1(event, nextFieldID) {
    if (event.key === "Enter") {
      let paid = parseFloat(document.getElementById('paid').value);
      let payable = parseFloat(document.getElementById('payable').value);

      if (paid > payable) {
        alert("Error: Paid amount is greater than the payable amount.");
      } else {
        document.getElementById(nextFieldID).focus();
      }

      event.preventDefault();
    }
  }*/
//paid is greater than payable
function checkPayment(paid, payable) {
    if (paid > payable) {
      console.log("Paid amount is greater than the payable amount.");
      alert("Paid amount is greater than the payable amount.");
      // Add your logic here for when paid is greater than payable
    } else {
      console.log("Paid amount is not greater than the payable amount.");
      // Add your logic here for other cases
    }
  }

