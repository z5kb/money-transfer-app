let paypalTransactions;

function renderProfile(userId) {
    // clear main and render the form
    $("#main").empty()
        .append('<form id="updateProfileForm" action="/h/settings" method="post"></form>');
    $("#updateProfileForm")
        .append('<h2>New e-mail</h2>')
        .append('<input id="new_email" type="text" name="new_email" placeholder="Type the current one if you do not want to change..." required>')
        .append('<h2>New password</h2>')
        .append('<input type="password" name="new_pass" placeholder="Type the current one if you do not want to change..." required>')
        .append('<br><br><input type="hidden" name="action" value="update profile">')
        .append('<input type="hidden" name="user_id" value=' + userId + '>')
        .append('<input type="submit" value="Done">');

    // init focus
    $("#new_email").focus();
}

function loadPaypalTransactions() {
    $.when(
        getPaypalTransactions()
    ).then(function() {
        renderPaypalTransactions();
    })
}

// get the users from the server
function getPaypalTransactions() {
    let deferred = $.Deferred();
    $.ajax({
        url: "http://127.0.0.1:5000/api/paypal_transactions",
        dataType: "json",
        type: "GET",
        success: function (result) {
            paypalTransactions = result;
            deferred.resolve();
        },
        error: function () {
            paypalTransactions = [];
            deferred.resolve();
        }
    });
    return deferred.promise();
}

function renderPaypalTransactions() {
    // clear main and create the transactions table
    $("#main").empty().append(
        '<div>' +
            '<table id="paypalTransactionsTable">' +
                '<tr class="header">' +
                    '<th onclick="sortTable(0)">Timestamp</th>' +
                    '<th onclick="sortTable(1)">Amount (EUR)</th>' +
                    '<th onclick="sortTable(2)">Status</th>' +
                '</tr>' +
            '</table>' +
        '</div>'
    );

    // render the transactions in the table
    for(let i = 0; i < paypalTransactions.length; i++) {
        $('#paypalTransactionsTable tr:last').after(
            '<tr>' +
            '<td>' + paypalTransactions[i][2] + '</td>' +
            '<td>' + paypalTransactions[i][0] + '</td>' +
            '<td>' + paypalTransactions[i][1] + '</td>' +
            '</tr>'
        );
    }
}

function sortTable(n) {
    let table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("paypalTransactionsTable");
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
