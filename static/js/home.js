let users;
let usersGotLoaded = 0;
let transferReceiverGotChosen = 0;
let ping;

function loadUsers() {
    $.when(
        getUsers()
    ).then(function() {
        renderUsers();
    })
}

// get the users from the server
function getUsers() {
    let deferred = $.Deferred();
    $.ajax({
        url: "http://127.0.0.1:5000/api/users",
        dataType: "json",
        type: "GET",
        success: function(result) {
            users = result;
            deferred.resolve();
        },
        error: function() {
            users = [];
            deferred.resolve();
        }
    });
    return deferred.promise();
}

// render the users on the page
function renderUsers() {
    for(let i = 0; i < users.length; i++) {
        $('#usersTable tr:last').after('<tr><td style="width: 15%">' +
            '<button type="button" onclick="addUserToTransferReceivers(' + i + ')">Add</button>' +
            '</td><td>' + users[i][1] + '</td></tr>');
    }
    usersGotLoaded = 1;
}

function addUserToTransferReceivers(i) {
    if(transferReceiverGotChosen === 1) {
        $("#transferReceiver").remove();
        $("#user2_id").remove();
    } else {
        $("#emptySetPlaceholder").remove();
        $("#transferReceiversHeader").text("Transfer receivers 1/1");
        transferReceiverGotChosen = 1;
    }
    $("#newTransactionForm").append('<input id="user2_id" type="hidden" name="user2_id" value="' + users[i][0] + '">');
    $('<p id="transferReceiver">' + users[i][1] + '</p>').appendTo("#transferReceiversDiv");
}

// dynamically search through users
function dynamicSearch() {
    let input = document.getElementById("searchUsersInput");
    let filter = input.value.toLowerCase();
    let table = document.getElementById("usersTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 0; i < rows.length; i++) {
        let td = rows[i].getElementsByTagName("td")[1];
        if (td) {
            let txtValue = td.textContent || td.innerText;
            if (txtValue.toLowerCase().indexOf(filter) > -1) {
                rows[i].style.display = "";
            } else {
                rows[i].style.display = "none";
            }
        }
    }
}

// function refreshPage() {
//     setInterval(function() {
//         while(1) {
//             $.when(
//                 pingServer()
//             ).then(function() {
//                 if(ping === 1) {
//                     window.location.reload(true)
//                 } else {
//                     ping = 0
//                 }
//             })
//         }
//     }, 5000)
// }
//
// // get the users from the server
// function pingServer() {
//     let deferred = $.Deferred();
//     $.ajax({
//         url: "http://127.0.0.1:5000/api/ping",
//         dataType: "json",
//         type: "GET",
//         success: function(result) {
//             ping = result;
//             deferred.resolve();
//         },
//         error: function() {
//             ping = "error";
//             deferred.resolve();
//         }
//     });
//     return deferred.promise();
// }

// toggle the visibility of the settingsDropdownContents div
function toggleSettingsDropdownContentsVisibility() {
    document.getElementById("settingsDropdownContents").classList.toggle("showSettingsDropdownContents");
}

// hide the settingsDropdownContents div if the user clicks outside of it
window.onclick = function (event) {
    if (!event.target.matches('.settingsDropdownButton')) {
        let dropdowns = document.getElementsByClassName("settingsDropdownContents");
        let i;
        for (i = 0; i < dropdowns.length; i++) {
            let openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('showSettingsDropdownContents')) {
                openDropdown.classList.remove('showSettingsDropdownContents');
            }
        }
    }
}

function openForm() {
    document.getElementById("myForm").style.display = "block";
    if(usersGotLoaded === 0) {
        loadUsers();
    }
}

function closeForm() {
    document.getElementById("myForm").style.display = "none";
}

function hideFlashedMessages() {
    setTimeout(function() {
        $("#flashedMessagesDiv").remove();
    }, 3000);
}