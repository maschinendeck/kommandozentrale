var app = angular.module('Kommandozentrale', ["ui.bootstrap", 'ngAnimate']);

app.controller('MainController', ['$scope', function ($scope) {
    $scope.init = function() {
        $scope.page = "html/control.html"
        $scope.socket = null;
        $scope.isopen = false;
        $scope.musicBtn = [["play","play"], ["pause","pause"], ["previous","backward"], ["next","forward"]]
        initSocket();
    }

    function initSocket() {
        $scope.socket = new WebSocket("ws://127.0.0.1:9000");
        $scope.socket.binaryType = "arraybuffer";
        $scope.socket.onopen = function() {
            console.log("Connected!");
            $scope.isopen = true;
            $scope.$apply();
            getConfig();
        }
        $scope.socket.onmessage = function(e) {
            var result = JSON.parse(e.data);

            console.log(e.data);

            if(result["result"] === "state") {
                onState(result["switch"], result["state"]);
            }

            if(result["result"] === "config") {
                $scope.config = result["config"];
            }

            $scope.$apply();
        }
        $scope.socket.onclose = function(e) {
            console.log("Connection closed.");
            $scope.socket = null;
            $scope.isopen = false;
            $scope.$apply();
        }

    }
    $scope.lightClick = function(event) {
        light = angular.element(event.target);
        switch_light(event.target.getAttribute("data-topic"), !light.hasClass("on"));
    };
    $scope.musicClick = function(event) {
        music = angular.element(event.target.parentNode);
        action = event.target.getAttribute("data-topic")
        switch_name = music[0].getAttribute("data-topic")
        callMethod(switch_name, action);

    };

    function onState(switchname, state) {
        $scope.config[switchname].state = state;
        $scope.$apply();
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

    function callMethod(data_switch, data_method, data) {
        data = {"action":"call_method", "switch":data_switch, "method":data_method, "data":data};
        sendData(data);
    }

    $scope.init();

}]);