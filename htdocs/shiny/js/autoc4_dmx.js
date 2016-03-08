var pickers = { plenar: {}, fnord: {}, wohnzimmer: {} };
function init_dmx() {
    pickers.plenar.master = $("#dmxcolorplenar-master");
    pickers.plenar.decke = $("#dmxcolorplenar-vorne1");
    pickers.plenar.heizung = $("#dmxcolorplenar-vorne2");

    $('.dmxinput').change(dmx_change);
    $('.btn-fade').click(dmx_fade);
    $('.btn-rand').click(dmx_rand);
    $('.btn-sound').click(dmx_sound);
}

function mqtt_subscribe_dmx() {
    mqtt_client.subscribe('dmx/+/+');
}

function mqtt_on_dmx_message(message) {
    var name = message.destinationName.split('/');
    var room = name[1];
    var picker = (pickers[room] || {})[name[2]];
    if (!picker) { return; }
    var payloadBytes = message.payloadBytes;
    if (payloadBytes.length >= 3) {
        var color = "#" + dec2hex(payloadBytes[0]) + dec2hex(payloadBytes[1]) + dec2hex(payloadBytes[2]);
        // update DMX picker values
        picker.val(color);

        var same = true;
        for (var light in pickers[room]) {
            if (light == "master") { continue; }
            same = same && (pickers[room][light].val() == color);
        }
        if (same) {
            pickers[room].master.val(color);
        }
    }

    if (payloadBytes.length == 7) {
        var speed = payloadBytes[4];
        if (speed === 0) { speed = 100; }
        $("#dmxfade" + room + " > .dmxspeed").val(speed);
    }
}

function dmx_change(e) {
    var dmx = $(this);
    var topic = dmx.data("topic");
    var color = dmx.val();
    var send_dmx_data;
    if (!topic.contains("fnord")) {
        send_dmx_data = send_dmx_data_7ch;
    } else {
        send_dmx_data = send_dmx_data_3ch;
    }
    if (topic.startsWith("dmx/")) {
        send_dmx_data(topic, color);
        return;
    }
    for (var light in pickers[topic]) {
        if (light == "master") { continue; }
        send_dmx_data("dmx/" + topic + "/" + light, color);
    }
}

function dmx_fade(e) {
    var dmx = $(this);
    var topic = dmx.data("topic");
    var speed = parseInt(dmx.siblings(".dmxspeed").val());
    for (var light in pickers[topic]) {
        if (light == "master") { continue; }
        send_dmx_fade_7ch("dmx/" + topic + "/" + light, speed);
    }
}

function hsv_to_rgb(h, s, v) {
    var h_i = Math.floor(h*6);
    var f = h*6 - h_i;
    var p = v * (1 - s);
    var q = v * (1 - f*s);
    var t = v * (1 - (1 - f) * s);
    switch (h_i) {
        case 0:
            r = v;
            g = t;
            b = p;
            break;
        case 1:
            r = q;
            g = v;
            b = p;
            break;
        case 2:
            r = p;
            g = v;
            b = t;
            break;
        case 3:
            r = p;
            g = q;
            b = v;
            break;
        case 4:
            r = t;
            g = p;
            b = v;
            break;
        case 5:
            r = v;
            g = p;
            b = q;
            break;
    }
    return [Math.floor(r*255), Math.floor(g*255), Math.floor(b*255)];
}

function dmx_rand(e) {
    var dmx = $(this);
    var topic = dmx.data("topic");
    var send_dmx_data;
    if (!topic.contains("fnord")) {
        send_dmx_data = send_dmx_data_7ch;
    } else {
        send_dmx_data = send_dmx_data_3ch;
    }

    var v = parseFloat(dmx.siblings(".dmxbright").val());
    for (var light in pickers[topic]) {
        if (light == "master") { continue; }
        var rgb = hsv_to_rgb(Math.random(), 0.8, v);
        var rgb_s = "#" + dec2hex(rgb[0]) + dec2hex(rgb[1]) + dec2hex(rgb[2]);
        send_dmx_data("dmx/" + topic + "/" + light, rgb_s);
    }
}

function dmx_sound(e) {
    var dmx = $(this);
    var topic = dmx.data("topic");
    for (var light in pickers[topic]) {
        if (light == "master") { continue; }
        send_dmx_sound_7ch("dmx/" + topic + "/" + light);
    }
}

// publish dmx rgb color + enable byte for a dmx room container
function send_dmx_data_3ch(topic, value) {
    var r = parseInt(value.substr(1, 2), 16);
    var g = parseInt(value.substr(3, 2), 16);
    var b = parseInt(value.substr(5, 2), 16);
    var buf = new Uint8Array([r, g, b, 255]);
    var message = new Messaging.Message(buf);
    message.retained = true;
    message.destinationName = topic;
    mqtt_client.send(message);
}

function send_dmx_data_7ch(topic, value) {
    var r = parseInt(value.substr(1, 2), 16);
    var g = parseInt(value.substr(3, 2), 16);
    var b = parseInt(value.substr(5, 2), 16);
    var buf = new Uint8Array([r, g, b, 0, 0, 0, 255]);
    var message = new Messaging.Message(buf);
    message.retained = true;
    message.destinationName = topic;
    mqtt_client.send(message);
}

function send_dmx_sound_7ch(topic) {
    var buf = new Uint8Array([0, 0, 0, 0, 255, 246, 255]);
    var message = new Messaging.Message(buf);
    message.retained = true;
    message.destinationName = topic;
    mqtt_client.send(message);
}

function send_dmx_fade_7ch(topic, speed) {
    if (speed > 255) { speed = 255; }
    var buf = new Uint8Array([0, 0, 0, 0, speed, 140, 255]);
    var message = new Messaging.Message(buf);
    message.retained = true;
    message.destinationName = topic;
    mqtt_client.send(message);
}
