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
    document.querySelector("#sidebar").classList.toggle("expand");
 }

  // Submenu Button  
  function sidebarBtn1(button) {
    // var element = document.getElementsByClassName("sub-menu");
     //element.classList.toggle("show");    
     document.querySelector(".sub-item").classList.toggle("show");
  }
 
  $(function(){
    // toggle sidebar collapse
    $('.btn-toggle-sidebar').on('click', function(){
        $('.wrapper').toggleClass('sidebar-collapse');
    });
    // mark sidebar item as active when clicked
    $('.sb-item').on('click', function(){
        if ($(this).hasClass('btn-toggle-sidebar')) {
          return; // already actived
        }
        $(this).siblings().removeClass('active');
        $(this).siblings().find('.sb-item').removeClass('active');
        $(this).addClass('active');
    })
  });