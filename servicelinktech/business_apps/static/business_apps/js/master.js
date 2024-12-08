function myFunction(x) {
    if (x.matches) { // If media query matches
      document.body.style.backgroundColor = "yellow";
      document.querySelector("#navbarToggleExternalContent").classList.remove("show");
      document.querySelector("#sidebar").classList.add("expands");
    } else {
      document.body.style.backgroundColor = "pink";
      document.querySelector("#navbarToggleExternalContent").classList.add("show");
      //document.querySelector("#side-nav").classList.add("condense");
    }
  }
  
  // Create a MediaQueryList object
  var x = window.matchMedia("(max-width: 575px)")
  
  // Call listener function at run time
  myFunction(x);
  
  // Attach listener function on state changes
  x.addEventListener("change", function() {
    myFunction(x);
  });

  // Sidenav Button  
  function sidebarBtn() {
    var element = document.getElementById("side-nav");
    element.classList.toggle("condense");
 }