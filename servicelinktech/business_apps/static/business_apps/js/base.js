/* const hmaburger = document.querySelector("#toggle-btn1");
hmaburger.addEventListener("click", function(){
    document.querySelector("#sidebar1").classList.toogle("expand");
    
})
*/
function sidebarBtn1() {
    var element = document.getElementById("sidebar");
    element.classList.toggle("expand");
 }

function myFunction(x) {
    if (x.matches) { // If media query matches
      document.body.style.backgroundColor = "yellow";
      document.querySelector("#sidebar").classList.add("expand");
    } else {
      document.body.style.backgroundColor = "pink";
      document.querySelector("#nav-body").classList.add("show");
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
