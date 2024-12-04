function sidebarBtn() {
    var x = document.getElementById("toggle-btn");
    if (x.style.display === "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }
  }

  function sidebarBtn1() {
    var element = document.getElementById("sidebar");
    element.classList.toggle("expand");
 }