 function toggleSubMenu(button){
  //button.nextElementSiblings.classList.toggle('show');
  var dropdownBtn = document.querySelectorAll(".dropdown-btn");
  const drop_container = document.querySelectorAll(".sub-menu");
  //Add this for toggling dropdown
  lastOpened = null;
  
  dropdownBtn.forEach(btn => btn.addEventListener('click', function() {      
    var menuContent = this.nextElementSibling;
    drop_container.forEach(b => b.classList.remove("show"));
    menuContent.classList.toggle("show");  
   
  }));
}
  // Sidenav Button  
  function sidebarBtn(button) {
   // var element = document.getElementsByClassName("sub-menu");
    //element.classList.toggle("show");    
    document.querySelector("#side-nav").classList.toggle("condense");
 }

 