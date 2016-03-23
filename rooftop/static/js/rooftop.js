function innlineEdit(orig,callback){
    var type = $(orig).attr('type');
    console.log($(orig))
    if(type == "addMember"){
        var userlist=$(orig).parent().parent().find('select');
        var ulList = $(orig).parent().parent().find('ul');
        var loader = $(orig).parent().parent().find('div').css("class","loader");
        //console.log("show select")
        //console.log(userlist)

        // remove all users which are already in the list
        $(ulList).children().each(function(index1,data){
            $(userlist).children().each(function(index2,data2){
                //console.log($(data).text().trim()+"=="+$(data2).text().trim())
                if($(data).text().trim()==$(data2).val().trim()){
                            $(data2).remove();
                            //FIXME: What is if i delete a user and want to add it again in the same pageload
                            //       Idea: show all first and hide all again
                            //$(data2).hide();
                }
            });
        });

        if($(userlist).children().size()>0){
            $(userlist).removeClass("hidden");
            $(userlist).show();
            $(userlist).click(function(){
                $(loader).removeClass("hidden");
                $(loader).show();
                $(userlist).hide();

                addUserToGroup($(orig).attr("groupid"),userlist.val(),function(result){
                    //console.log(result)
                    //console.log($(orig).parent().parent().find('ul'))
                    if(result){
                        var check=false;
                        //console.log(ulList)
                        $(ulList).children().each(function(elem,data){
                            if($(data).text().trim()==userlist.val()){
                                check=true;
                            }
                        });
                        if(check==false){
                            ulList.append($('<li>'+userlist.val()+' <span class="glyphicon glyphicon-ok"></span></li>'))
                        }
                        $(loader).hide();
                    }
                });

            });
        }else{
            var msg=$("<p>Alle User sind in dieser Gruppe vorhanden</p>");
            $(ulList).parent().append(msg);
            msg.fadeOut(4000,function(){
                msg.remove();
            })
        }
    }
}

function addUserToGroup(groupname,username,callback){
    param = {}
    param['modGroupname']=groupname;
    param['addUser']=username;
    sendPostQuery("modGroup/",param,function(data){
        callback(data);
    });
}

function sendPostQuery(query,param,callback,type){
    if (typeof type === "undefined" || type === null) {
        type = "json";
    }
    param['csrfmiddlewaretoken'] = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    //param['monthID'] = document.getElementsByName('monthID')[0].value;
    $.ajax({
        url : query,
        type: "POST",
        data : param,
        dataType : type,
        success: function(data){
            callback(data);
        }
    });
}

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

    $('.add-user-to-group').click(function(){
        //var elem = $(this);
        var elem = $(this).parent().find('select');
        console.log(elem)
        var userName=$(elem).val();
        var groupName=$(elem).attr('groupid');
        param = {}
        param['modGroupname']=groupName;
        param['addUser']=userName;
        sendPostQuery("/mod/group/",param,function(data){
            elem.append($('<i class="glyphicon glyphicon-ok">'))
        });
    });
});
