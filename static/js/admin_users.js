let users;

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
        url: "http://127.0.0.1:5000/api/a/users",
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
        $('#usersTable tr:last').after('<tr>' +
            '<td>' + users[i][0] + '</td>' +
            '<td>' + users[i][1] + '</td>' +
            '<td>' + users[i][3] + '</td>' +
            '<td>' + users[i][2] + '</td>' +
            '<td style="width: 5%"><button type="button" onclick="updateUser(' + i + ')">Update</button></td>' +
            '<td style="width: 5%"><button type="submit" onclick="freezeUser(' + users[i][0] + ')">Freeze</button></td>' +
            '<td style="width: 5%"><button type="submit" onclick="unfreezeUser(' + users[i][0] + ')">Unfreeze</button></td>' +
            '<td style="width: 5%"><button type="submit" onclick="deleteUser(' + users[i][0] + ')">Delete</button></td>' +
            + '</tr>'
        );
    }
}

// delete user
function deleteUser(userId) {
    // set form action to delete
    $("#usersTableForm").attr("action", "/api/a/delete_user")
        .append('<input type="hidden" name="user_id" value="' + userId + '">');
}

// freeze user
function freezeUser(userId) {
    // set form action to delete
    $("#usersTableForm").attr("action", "/api/a/freeze_user")
        .append('<input type="hidden" name="user_id" value="' + userId + '">');
}

function unfreezeUser(userId) {
    // set form action to delete
    $("#usersTableForm").attr("action", "/api/a/unfreeze_user")
        .append('<input type="hidden" name="user_id" value="' + userId + '">');
}

// update user
function updateUser(i) {
    $("#updateUserFormHeader").text("Update " + users[i][1]);
    $("#newEmailInput").val(users[i][1]);
    $("#newRoleInput").val(users[i][2]);
    $("#newBalanceInput").val(users[i][3]);
    $("#userId").val(users[i][0]);
    $("#updateUserForm").show();
}

function closeUpdateUserForm() {
    $("#updateUserForm").hide();
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

function sortTable(n) {
    let table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("usersTable");
    switching = true;

    //Set the sorting direction to ascending:
    dir = "asc";

    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
        //start by saying: no switching is done:
        switching = false;
        rows = table.rows;

        /*Loop through all table rows (except the
        first, which contains table headers):*/
        for (i = 1; i < (rows.length - 1); i++) {
            //start by saying there should be no switching:
            shouldSwitch = false;

            /*Get the two elements you want to compare,
            one from current row and one from the next:*/
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];

            /*check if the two rows should switch place,
            based on the direction, asc or desc:*/
            if (dir === "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    //if so, mark as a switch and break the loop:
                    shouldSwitch= true;
                    break;
                }
            } else if (dir === "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    //if so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /*If a switch has been marked, make the switch
            and mark that a switch has been done:*/
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;

            //Each time a switch is done, increase this count by 1:
            switchcount ++;
        } else {
            /*If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again.*/
            if (switchcount === 0 && dir === "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}