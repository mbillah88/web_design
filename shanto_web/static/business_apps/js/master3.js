function myFunction(x) {
    if (x.matches) { // If media query matches
      document.body.style.backgroundColor = "yellow";
      document.querySelector("#side-nav").classList.remove("condense");
    } else {
      document.body.style.backgroundColor = "pink";
      //document.querySelector("#nav-body").classList.add("show");
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
  function sidebarBtn(button) {
    // var element = document.getElementsByClassName("sub-menu");
     //element.classList.toggle("show");    
     document.querySelector("#side-nav").classList.toggle("condense");
  }

  // Sidenav DropDown Button  
  function sidebarDropBtn(button) {
    // var element = document.getElementsByClassName("sub-menu");
     //element.classList.toggle("show");    
     document.querySelectorAll(".sub-menu").classList.toggle("show");
     document.getElementsByTagName("BODY")[0].style.backgroundColor = "yellow";
  }
 
 