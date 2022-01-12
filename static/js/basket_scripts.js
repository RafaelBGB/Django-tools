"use strict";

window.onload = function () {
    $('.basket_list').on('change', "input[type='number']", function (event) {
        console.log('OK')
        let t_href = event.target;
        $.ajax({
            url: "/basket/edit/" + t_href.name + "/" + t_href.value + "/",
            success: function(data){
            $('.basket_list').html(data.result);
            },
        });
    });
}
