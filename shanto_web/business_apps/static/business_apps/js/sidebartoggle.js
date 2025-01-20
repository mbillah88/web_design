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