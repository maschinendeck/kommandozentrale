function init_light() {
    $(".btn-light").click(function (e) {
        var light = $(this);
        switch_light(light.data("topic"), !light.hasClass("on"));
    });
}

function on_light_message(switchname, state) {
    // update .btn-light state
    var button = $('.btn-light').filter('[data-topic="' + switchname + '"]');
    if (button && state) {
        button.addClass('on');
    } else {
        button.removeClass('on');
    }
}

// publish (on ? 0x01 : 0x00) message to a topic
function switch_light(topic, on) {

    if(on) {
        var state = "on";
    } else {
        var state = "off";
    }

    sendData("call_method", topic, state)
}
