
var socket = null;
var isopen = false;
window.onload = function() {
    socket = new WebSocket("ws://127.0.0.1:9000");
    socket.binaryType = "arraybuffer";
    socket.onopen = function() {
       console.log("Connected!");
       isopen = true;
       initLights();
    }
    socket.onmessage = function(e) {
        console.log("Text message received: " + e.data);
        var result = JSON.parse(e.data);

        if(result["result"] == "state") {
            on_light_message(result["switch"], result["state"]);
        }


        if(result["result"] == "config") {
            addButtons(result["config"]);
        } 

        
    }
    socket.onclose = function(e) {
       console.log("Connection closed.");
       socket = null;
       isopen = false;
    }


    initLights();


 };

function initLights() {
    //add buttons
    if (isopen) {
       var jsonstring = JSON.stringify({"action":"get_config"})
       socket.send(jsonstring);
       console.log("Text message sent: " + jsonstring);
    } else {
       console.log("Connection not opened.")
    }
}


function addButtons(config) {
    //add buttons
    $(".lightswitch-pane").each(function() {
console.log(config);
    // go thru the main array
    for (var key in config) {
        // go thru the inner arrays
        console.log("Do");
        $(".lightswitch-pane").append($('<button type="button" class="btn btn-light" data-topic="'+ key +'"></button>', { class: 'alpha_li', text: config[key]["name"] }));
    }       
});
}



 function sendData(data_action, data_switch, data_method) {
    if (isopen) {

       var jsonstring = JSON.stringify({"action":data_action, "switch":data_switch,"method":data_method})

       socket.send(jsonstring);
       console.log("Text message sent: " + jsonstring);               
    } else {
       console.log("Connection not opened.")
    }
 };
 




function update_time() {
    var now = new Date();
    var text = two_digits(now.getDate()) + "." + two_digits(now.getMonth() + 1) + "." + now.getFullYear() + " " + two_digits(now.getHours()) + ":" + two_digits(now.getMinutes());
    $('#datetime').text(text);
    setTimeout(update_time, 60000 - now.getSeconds() * 1000 - now.getMilliseconds());
}

$(function() {
    $('#shutdown').click(function(ev) {
        
    });

    $('#shutdown-force').click(function(ev) {
        
    });

    $('#gate').click(function(ev) {
        
    });

    $('#help').click(function(ev) {
        ev.preventDefault();
        $('#help-display').toggle();
    });

    update_time();
    init_light();
    init_dmx();
});
