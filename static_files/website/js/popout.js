$( document ).ready(function() {
    $(".popout .popout-btn").click(function() {
        $(this).toggleClass("active");
        $(this).closest(".popout").find(".panel").toggleClass("active");
    });
    $(".popout .popout-btn").click(function(event) {
        event.stopPropagation();
    });
    $(".popout .close").click(function() {
        $(".popout .panel").removeClass("active");
        $(".popout .popout-btn").removeClass("active");
    });
});  
