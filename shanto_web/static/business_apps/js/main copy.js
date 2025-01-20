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
    //button.nextElementSibling.classList.toggle('show')
    //button.classList.toggle('rotate')
    
      const content = button.nextElementSibling; 
      // Close any open content 
      document.querySelectorAll('.content').forEach(item => { 
        if (item !== content && item.style.display === "block") { 
          item.style.display = "none"; 
        } 
        }); 
        // Toggle the clicked content 
          if (content.style.display === "none" || !content.style.display) { 
            content.style.display = "block"; 
          } else { 
              content.style.display = "none"; 
            } 
            
  }
     
       
   // Sidenav Button Submenu................ drop-down
    document.addEventListener("DOMContentLoaded", function() { 
      const buttons = document.querySelectorAll(".toggle-btn"); 
      buttons.forEach(button => { 
        button.addEventListener("click", function() { 
          const targetId = button.getAttribute("data-target"); 
          const content = document.getElementById(targetId);  
          // Close any open content 
            document.querySelectorAll('.sub-item').forEach(item => { 
              if (item !== content) { 
                item.classList.remove("show");
                button.classList.remove('rotate');
              } 
              
            }); 
            // Toggle the clicked content 
            if (!targetId){
              // Not anything 

            }else{
              if (content.style.display === "none" || !content.style.display) { 
                  //content.style.display = "block"; 
                  content.classList.add("show");
                  button.classList.add('rotate')
              } else { 
                  content.classList.remove("show");
                }
              }
              button.classList.add('rotate');
            }); 
          });
        });

 
// Add active class to the current button (highlight it)
var btns = document.getElementsByClassName("sidebar-link");
for (var i = 0; i < btns.length; i++) {
  btns[i].addEventListener("click", function() {
  var current = document.getElementsByClassName("active");
  current[0].className = current[0].className.replace(" active", "");
  this.className += " active";
  });
}
  

 
// Add Body Behavior............
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
