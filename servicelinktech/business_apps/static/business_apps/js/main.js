// Sidenav Button  
function sidebarBtn(button) {
   // var element = document.getElementsByClassName("sub-menu");
    //element.classList.toggle("show");    
    document.querySelector("#sidebar").classList.toggle("nav-side-bar");
 }
 // Sidenav Button  
function sidebarBtnNav(button) {
   // var element = document.getElementsByClassName("sub-menu");
    //element.classList.toggle("show");    
    document.querySelector(".side-nav-body").classList.toggle("colaps");
 }

   // Sidenav Button  
   function sidebarBtn1(button) {
     // var element = document.getElementsByClassName("sub-menu");
      //element.classList.toggle("show");    
      document.querySelector(".sub-item").classList.toggle("show");
      document.querySelector(".drop-btn").classList.toggle("rotate");
   }
              
   
function myFunction(x) {
   if (x.matches) { // If media query matches
     document.body.style.backgroundColor = "yellow";
     document.querySelector("#sidebar").classList.add("nav-side-bar");
     document.querySelector(".side-nav-body").classList.add("colaps");
   } else {
     document.body.style.backgroundColor = "pink";
     document.querySelector(".side-nav-body").classList.remove("colaps");
     document.querySelector("#sidebar").classList.add("nav-side-bar");
   }
 }
 
 // Create a MediaQueryList object
 var x = window.matchMedia("(max-width: 600px)")
 
 // Call listener function at run time
 myFunction(x);
 
 // Attach listener function on state changes
 x.addEventListener("change", function() {
   myFunction(x);
 });
