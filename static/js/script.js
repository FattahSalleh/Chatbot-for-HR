// ========================== Greet user when widget loads ========================
$(document).ready(function() {

    //if you want the bot to start the conversation
    action_trigger();

})

// ========================== Let the bot start the conversation ========================
function action_trigger() {

    //Greet the user
    var greetMsg = "Hello! I am Chatbot for HR.";

    showBotTyping();

    //display bot response after 500 milliseconds
    hideBotTyping();

    //check if the response contains "text"
    var BotResponse = '<img class="botAvatar" src="../static/img/botAvatar.png"/><p class="botMsg">' + greetMsg + '</p><div class="clearfix"></div>';
    $(BotResponse).appendTo(".chats").hide().fadeIn(1000);

    scrollToBottomOfResults();
}



// ========================== Log out message ========================
function logout() {

    var logoutMsg = "Logged out!";

    showBotTyping();

    //display bot response after 500 milliseconds
    hideBotTyping();

    //check if the response contains "text"
    var BotResponse = '<img class="botAvatar" src="../static/img/botAvatar.png"/><p class="botMsg">' + logoutMsg + '</p><div class="clearfix"></div>';
    $(BotResponse).appendTo(".chats").hide().fadeIn(1000);

    scrollToBottomOfResults();

}



//=====================================	User enter or sends the message =====================
$(".usrInput").on("keyup keypress", function(e) {
    var keyCode = e.keyCode || e.which;

    var text = $(".usrInput").val();
    if (keyCode === 13) {

        if (text == "" || $.trim(text) == "") {
            e.preventDefault();
            return false;
        } else {
            $(".usrInput").focus();
            setUserResponse(text);
            send(text);
            e.preventDefault();
            return false;
        }
    }
});

$("#sendButton").on("click", function(e) {
    var text = $(".usrInput").val();
    if (text == "" || $.trim(text) == "") {
        e.preventDefault();
        return false;
    } else {
        $(".usrInput").focus();
        setUserResponse(text);
        send(text);
        e.preventDefault();
        return false;
    }
})

//==================================== Set user response =====================================
function setUserResponse(message) {
    var UserResponse = '<img class="userAvatar" src=' + "../static/img/userAvatar.jpg" + '><p class="userMsg">' + message + ' </p><div class="clearfix"></div>';
    $(UserResponse).appendTo(".chats").show("slow");

    $(".usrInput").val("");
    scrollToBottomOfResults();
    showBotTyping();
    $(".suggestions").remove();
}

//=========== Scroll to the bottom of the chats after new message has been added to chat ======
function scrollToBottomOfResults() {

    var terminalResultsDiv = document.getElementById("chats");
    terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

//============== send the user message to Flask server =========================================
function send(message) {
    $.get("/get", { ui: message }).done(function(data) {


        // if user wants to logout and clear the existing chat contents
        if (message.toLowerCase() == '/logout') {
            $("#userInput").prop('disabled', false);
            $(".chats").html("");
            $(".usrInput").val("");

            //if you want the bot to start the conversation after restart
            logout();
            action_trigger();

            return;
        }

        setBotResponse(data);

        //DEBUGGIN STUFF
        // alert(data);
        // console.log(data);
    });
}





//=================== Set bot response in the chat ===========================================
function setBotResponse(response) {

    //display bot response after 500 milliseconds
    setTimeout(function() {
        hideBotTyping();

        //check if the response contains "text"
        var BotResponse = '<img class="botAvatar" src="../static/img/botAvatar.png"/><p class="botMsg">' + response + '</p><div class="clearfix"></div>';
        $(BotResponse).appendTo(".chats").hide().fadeIn(1000);



        scrollToBottomOfResults();

    }, 500);
}

//====================================== Toggle chatbot =======================================
$("#profile_div").click(function() {
    $(".profile_div").toggle();
    $(".widget").toggle();
    $(".usrInput").focus();
});


//====================================== Functions for the bot widget  =========================================

//close function to close the widget.
$("#close").click(function() {
    $(".profile_div").toggle();
    $(".widget").toggle();
    scrollToBottomOfResults();
});



//====================================== Bot typing animation ======================================
function showBotTyping() {

    var botTyping = '<img class="botAvatar" id="botAvatar" src="../static/img/botAvatar.png"/><div class="botTyping">' + '<div class="bounce1"></div>' + '<div class="bounce2"></div>' + '<div class="bounce3"></div>' + '</div>'
    $(botTyping).appendTo(".chats");
    $('.botTyping').show();
    scrollToBottomOfResults();
}

function hideBotTyping() {
    $('#botAvatar').remove();
    $('.botTyping').remove();
}