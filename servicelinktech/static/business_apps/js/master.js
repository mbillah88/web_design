function myFunction(x) {
    if (x.matches) { // If media query matches
      document.body.style.backgroundColor = "yellow";
      document.querySelector("#navbarToggleExternalContent").classList.remove("show");
    } else {
      document.body.style.backgroundColor = "pink";
      document.querySelector("#navbarToggleExternalContent").classList.add("show");
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