$(document).ready(function () {

    var panels = $('.info');
    var panelsButton = $('.dropdown-info');
    panels.hide();
    //Click dropdown
    panelsButton.click(function() {
        //get data-for attribute
        var dataFor = $(this).attr('data-for');
        var idFor = $(dataFor);

        //current button
        var currentButton = $(this);
        idFor.removeClass("hidden");
        idFor.slideToggle(400, function() {
            //Completed slidetoggle
            if(idFor.is(':visible'))
            {
                if(dataFor != ".addUser" && dataFor != ".addGroup"){
                    currentButton.html('<i class="glyphicon glyphicon-chevron-up text-muted"></i>');
                }
            }
            else
            {
                if(dataFor != ".addUser" && dataFor != ".addGroup"){
                    currentButton.html('<i class="glyphicon glyphicon-chevron-down text-muted"></i>');
                }
            }
        })
    });
});
