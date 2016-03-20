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

    //$("#addUser").click(function(event){
    //   addUser();
    //});

    $('form[name=userform]').submit(function(){
        // Maybe show a loading indicator...
        $.post($(this).attr('action'), $(this).serialize(), function(res){
            // Do something with the response `res`
            // Don't forget to hide the loading indicator!
            console.log(res);
            $('.addUser').slideToggle(400,function(){});
            if(res){
              location.reload();
            }
        });
        return false; // prevent default action
    });

    $('form[name=groupform]').submit(function(){
        // Maybe show a loading indicator...
        $.post($(this).attr('action'), $(this).serialize(), function(res){
            // Do something with the response `res`
            // Don't forget to hide the loading indicator!
            console.log(res);
            $('.addGroup').slideToggle(400,function(){});
            if(res){
              location.reload();
            }
        });
        return false; // prevent default action
    });

    $("#cancelUser").click(function(event){
        $('.addUser').slideToggle(400,function(){
          //TODO clear fields
            //clearUserFields();
        });
    });

    $("#addGroup").click(function(event){
        addGroup();
    });

    $("#cancelGroup").click(function(event){
        $('.addGroup').slideToggle(400,function(){
          //TODO clear fields
            //clearGroupFields();
        });
    });
});
