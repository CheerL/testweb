function close_connection(close_url, client_id, channel,){
    if(window.socket){
        if(client_id){
            $.get(close_url + "/client_id=" + client_id + "&channel=" + channel, function(data){
                if (data.res == true){
                    console.log('Closing connection');
                }
                else if(data.res == false){
                    alert(data.msg);
                }
            });
        }
        window.socket.close();
        window.socket = null;
    }
}

function open_connection(test_url, open_url, client_id, channel, func){
    $.get(test_url + "/client_id=" + client_id + "&channel=" + channel, function(data){
        if(data.res == true){
            console.log('Client has connection');
        }
        else if(data.res == false){
            console.log(data.msg);
            client_id = data.client_id;
            var socket = new WebSocket("ws://" + window.location.host + open_url +
                                        "/client_id=" + client_id + "&channel=" + channel);
            socket.onopen = function () {
                console.log('WebSocket open');
            };
            socket.onmessage = function (message) {
                func(message);
            };
            window.socket = socket;
        }
    });
}

function send_message(message) {
    if(!window.socket){
        alert("Please connect");
    }else{
        window.socket.send(message);
    }
}