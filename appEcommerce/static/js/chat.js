var text_box = '<div class="card-panel right" style="width: 75%; position: relative">' +
        '<div style="position: absolute; top: 0; left:3px; font-weight: bolder" class="title">{sender}</div>' +
        '{message}' +
        '</div>';

function scrolltoend() {
    $('#board').stop().animate({
        scrollTop: $('#board')[0].scrollHeight
    }, 800);
}

function send(sender, receiver, message) {
    var data = {
        'sender': sender,
        'receiver': receiver,
        'message': message
    };

    console.log('Sender:', sender);
    console.log('Receiver:', receiver);

    $.ajax({
        url: '/api/messages/',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(data) {
            console.log(data);
            var box = text_box.replace('{sender}', "You");
            box = box.replace('{message}', message);
            $('#board').append(box);
            scrolltoend();
        },
        error: function(error) {
            console.error('Error sending message:', error);
        }
    });
}

function receive() {
    $.get('/api/messages/'+ sender_id + '/' + receiver_id, function (data) {
        console.log(data);
        if (data.length !== 0)
        {
            for(var i=0;i<data.length;i++) {
                console.log(data[i]);
                var box = text_box.replace('{sender}', data[i].sender);
                box = box.replace('{message}', data[i].message);
                box = box.replace('right', 'left blue lighten-5');
                $('#board').append(box);
                scrolltoend();
            }
        }
    })
}
