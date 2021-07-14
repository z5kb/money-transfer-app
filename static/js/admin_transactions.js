let transactions;

function loadTransactions() {
    $.when(
        getTransactions()
    ).then(function() {
        renderTransactions();
        $("#searchTransactionsInput").focus();
    })
}

// get the transactions from the server
function getTransactions() {
    let deferred = $.Deferred();
    $.ajax({
        url: "http://127.0.0.1:5000/api/a/transactions",
        dataType: "json",
        type: "GET",
        success: function(result) {
            transactions = result;
            deferred.resolve();
        },
        error: function() {
            transactions = [];
            deferred.resolve();
        }
    });
    return deferred.promise();
}

// render the transactions on the page
function renderTransactions() {
    for(let i = 0; i < transactions.length; i++) {
        $('#transactionsTable tr:last').after('<tr>' +
            '<td>' + transactions[i][0] + '</td>' +
            '<td>' + transactions[i][1] + '</td>' +
            '<td>' + transactions[i][2] + '</td>' +
            '<td>' + transactions[i][3] + '</td>' +
            '<td>' + transactions[i][4] + '</td>' +
            '<td>' + transactions[i][5] + '</td>' +
            '<td style="width: 5%"><button type="submit" onclick="freezeTransaction(' + transactions[i][0] + ')">Freeze</button></td>' +
            '<td style="width: 5%"><button type="submit" onclick="unfreezeTransaction(' + transactions[i][0] + ')">Unfreeze</button></td>' +
            + '</tr>'
        );
    }
}

// freeze transaction
function freezeTransaction(transactionId) {
    // set form action to delete
    $("#transactionsTableForm").attr("action", "/api/a/freeze_transaction")
        .append('<input type="hidden" name="transaction_id" value="' + transactionId + '">');
}

// unfreeze transaction
function unfreezeTransaction(transactionId) {
    // set form action to delete
    $("#transactionsTableForm").attr("action", "/api/a/unfreeze_transaction")
        .append('<input type="hidden" name="transaction_id" value="' + transactionId + '">');
}

// dynamically search through transactions
function dynamicSearch() {
    let input = document.getElementById("searchTransactionsInput");
    let filter = input.value.toLowerCase();
    let table = document.getElementById("transactionsTable");
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

function sortTable(n) {
    let table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("transactionsTable");
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
