let paypalTransactions;

function loadTransactions() {
    $.when(
        getTransactions()
    ).then(function() {
        renderTransactions();
        $("#searchPaypalTransactionsInput").focus();
    })
}

// get the transactions from the server
function getTransactions() {
    let deferred = $.Deferred();
    $.ajax({
        url: "http://127.0.0.1:5000/api/a/paypal_transactions",
        dataType: "json",
        type: "GET",
        success: function(result) {
            paypalTransactions = result;
            deferred.resolve();
        },
        error: function() {
            paypalTransactions = [];
            deferred.resolve();
        }
    });
    return deferred.promise();
}

// render the transactions on the page
function renderTransactions() {
    for(let i = 0; i < paypalTransactions.length; i++) {
        $('#paypalTransactionsTable tr:last').after('<tr>' +
            '<td>' + paypalTransactions[i][0] + '</td>' +
            '<td>' + paypalTransactions[i][5] + '</td>' +
            '<td>' + paypalTransactions[i][1] + '</td>' +
            '<td>' + paypalTransactions[i][2] + '</td>' +
            '<td>' + paypalTransactions[i][3] + '</td>' +
            '<td>' + paypalTransactions[i][4] + '</td>' +
            + '</tr>'
        );
    }
}

// dynamically search through transactions
function dynamicSearch() {
    let input = document.getElementById("searchPaypalTransactionsInput");
    let filter = input.value.toLowerCase();
    let table = document.getElementById("paypalTransactionsTable");
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
