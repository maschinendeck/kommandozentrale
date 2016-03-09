var app = angular.module('Kommandozentrale', ["ui.bootstrap", 'ngAnimate']);

app.controller('MainController', ['$scope', function ($scope) {
    init = function() {
        $scope.page = "html/control.html"
        $scope.socket = null;
        $scope.isopen = false;
        initSocket();
    }
    init()



    function initSocket() {
        $scope.socket = new WebSocket("ws://127.0.0.1:9000");
        $scope.socket.binaryType = "arraybuffer";
        $scope.socket.onopen = function() {
            console.log("Connected!");
            $scope.isopen = true;
            getConfig();
        }
        $scope.socket.onmessage = function(e) {
            var result = JSON.parse(e.data);

            if(result["result"] == "state") {
                on_light_message(result["switch"], result["state"]);
            }

            if(result["result"] == "config") {
                $scope.config = result["config"];
            }
        }
        $scope.socket.onclose = function(e) {
            console.log("Connection closed.");
            $scope.socket = null;
            $scope.isopen = false;
        }

    }
    $scope.lightClick = function(event) {
        light = angular.element(event.target);
        switch_light(event.target.getAttribute("data-topic"), !light.hasClass("on"));
    };
    function on_light_message(switchname, state) {
        var button = angular.element(document.querySelectorAll('[data-topic="' + switchname + '"]'));
        if (button && state) {
            button.addClass('on');
        } else {
            button.removeClass('on');
        }
    }

    function switch_light(topic, on) {
        callMethod(topic, on ? "on" : "off")
    }

    function getConfig() {
        sendData({"action":"get_config"});
    }

    function sendData(data) {
        if ($scope.isopen) {
            var jsonstring = JSON.stringify(data)
            $scope.socket.send(jsonstring);
            console.log("Text message sent: " + jsonstring);
        } else {
            console.log("Connection not opened.")
        }
    }

    function callMethod(data_switch, data_method) {
        data = {"action":"call_method", "switch":data_switch, "method":data_method};
        sendData(data);
    }

}]);
