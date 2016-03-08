function mqtt_subscribe_status() {
    mqtt_client.subscribe('club/status');
}

function mqtt_on_status_message(message) {
    var icon = $('#status .glyphicon');
    var text = $('#status :last-child');
    if (message.payloadBytes[0]) {
        icon.removeClass('glyphicon-hand-right')
            .removeClass('glyphicon-thumbs-down')
            .addClass('glyphicon-thumbs-up');
        icon.css('color', '#0c0');
        text.text('Open');
    } else {
        icon.removeClass('glyphicon-hand-right')
            .removeClass('glyphicon-thumbs-up')
            .addClass('glyphicon-thumbs-down');
        icon.css('color', '#c00');
        text.text('Closed');
    }
}
