/**
 * Created by lidad on 2017/6/25.
 */
window.onload=function () {
    $('.collapsible').collapsible();
            $('.modal').modal();
        $("#headimg").sideNav();
    $("#search").click(function () {
        var searchKey = $("#searchGzh").val();
        if (searchKey){
             window.location = document.domain+"?s="+searchKey
        }

    })
};