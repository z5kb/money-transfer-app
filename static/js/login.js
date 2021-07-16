function initFocus() {
    document.getElementById("email").focus();
}

function hideFlashedMessages() {
    setTimeout(function() {
        document.getElementById("flashedMessagesDiv").remove();
    }, 3000);
}
