let users;
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
    // TODO insert as table element, not plain text
    $("#usersTable").append(users[0])
}

// dynamically search through users
function dynamicSearch() {
    let input = document.getElementById("searchUsersInput");
    let filter = input.value.toLowerCase();
    let table = document.getElementById("usersTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 0; i < rows.length; i++) {
        let td = rows[i].getElementsByTagName("td")[0];
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