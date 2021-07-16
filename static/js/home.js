let users;
let usersGotLoaded = 0;
let transferReceiverGotChosen = 0;
let transactions;

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

function loadTransactions() {
    $.when(
        getTransactions()
    ).then(function() {
        renderTransactions();
    })
}

// get the users from the server
function getTransactions() {
    let deferred = $.Deferred();
    $.ajax({
        url: "http://127.0.0.1:5000/api/transactions",
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

// render the users on the page
function renderTransactions() {
    for(let i = 0; i < transactions.length; i++) {
        if(transactions[i][6] === "== user1") {
            prepareToRenderTransaction(transactions[i][3], transactions[i][4], transactions[i][5], transactions[i][0],
                transactions[i][1], 1);
        } else if(transactions[i][6] === "!= user1") {
            prepareToRenderTransaction(transactions[i][2], transactions[i][5], transactions[i][4], transactions[i][0],
                transactions[i][1], 0);
        }
    }
}

function prepareToRenderTransaction(otherPerson, currentUserChange, otherUserChange, transactionId, transactionStatus,
                                    currentUserIsInitiator) {
    let currentUserChangeBackup = currentUserChange;

    // append + in front of currentUserChange if it is not < 0
    if (currentUserChange.toString()[0] !== "-") {
        currentUserChange = "+ " + currentUserChange.toString();
    } else {
        let currentUserChangeWithoutMinus = currentUserChange.toString().slice(1);
        currentUserChange = "- " + currentUserChangeWithoutMinus
    }

    // append " " between the minus and otherUserChange if otherUserChange < 0
    if (otherUserChange.toString()[0] !== "-") {
        otherUserChange = "+ " + otherUserChange.toString();
    } else {
        let otherUserChangeWithoutMinus = otherUserChange.toString().slice(1);
        otherUserChange = "- " + otherUserChangeWithoutMinus
    }

    // render the transaction
    if(transactionStatus === "frozen") {
        renderTransaction(otherPerson, currentUserChange, otherUserChange, transactionId, currentUserChangeBackup,
            "cadetblue", "cadetblue", "cadetblue",
            "cadetblue", "background: cadetblue", currentUserIsInitiator, 0);
    } else if(transactionStatus === "accepted") {
        renderTransaction(otherPerson, currentUserChange, otherUserChange, transactionId, currentUserChangeBackup,
            "mediumseagreen", "mediumseagreen", "mediumseagreen",
            "mediumseagreen", "background: mediumseagreen", currentUserIsInitiator, 0);
    } else if(transactionStatus === "rejected") {
        renderTransaction(otherPerson, currentUserChange, otherUserChange, transactionId, currentUserChangeBackup,
            "indianred", "indianred", "indianred",
            "indianred", "background: indianred", currentUserIsInitiator, 0);
    } else {
        renderTransaction(otherPerson, currentUserChange, otherUserChange, transactionId, currentUserChangeBackup,
            "indianred", "mediumseagreen", "mediumseagreen",
            "indianred", "", currentUserIsInitiator, 1);
    }
}

function renderTransaction(otherPerson, currentUserChange, otherUserChange, transactionId, currentUserChangeBackup,
                                 backgroundOneOne, backgroundOneTwo, backgroundTwoOne, backgroundTwoTwo, trStyle,
                                 currentUserIsInitiator, transactionIsOpen) {
    if(transactionIsOpen === 1) {
        if (currentUserIsInitiator === 1) {
            // current user is the transfer initiator
            if (currentUserChangeBackup < 0) {
                renderOpenTransactionWhereUserIsInitiator(otherPerson, backgroundOneOne, currentUserChange,
                    transactionId, trStyle);
            } else {
                renderOpenTransactionWhereUserIsInitiator(otherPerson, backgroundOneTwo, currentUserChange,
                    transactionId, trStyle);
            }
        } else {
            // current user is NOT the transfer initiator
            if (currentUserChangeBackup < 0) {
                renderOpenTransactionWhereUserIsNotInitiator(otherPerson, backgroundOneOne, currentUserChange,
                    transactionId, trStyle);
            } else {
                renderOpenTransactionWhereUserIsNotInitiator(otherPerson, backgroundTwoOne, currentUserChange,
                    transactionId, trStyle);
            }
        }
    } else {
        // transaction is NOT open
        if (currentUserIsInitiator === 1) {
            // current user is the transfer initiator
            renderNotOpenTransaction(otherPerson, currentUserChangeBackup, backgroundOneOne,
                backgroundTwoOne, currentUserChange, transactionId, trStyle);
        } else {
            // current user is NOT the transfer initiator
            renderNotOpenTransaction(otherPerson, currentUserChangeBackup, backgroundOneOne,
                backgroundTwoOne, currentUserChange, transactionId, trStyle);
        }
    }
}

function renderOpenTransactionWhereUserIsInitiator(otherPerson, background, currentUserChange, transactionId, trStyle) {
    $('#transactionsTable tr:last').after(
        '<tr style="' + trStyle + '">' +
        '<td style="background: ' + background + '; opacity: 0.9">' + currentUserChange + ' EUR</td>' +
        '<td>' + otherPerson + '</td>' +

        '<td style="width: 12.5%"></td>' +

        '<td style="width: 12.5%">' +
        '<form action="/api/complete_transaction" method="post">' +
        '<button type="submit" style="width: 80%" name="answer" value="reject;' + transactionId + '">Reject</button>' +
        '</form>' +
        '</td>' +
        '</tr>'
    );
}

function renderOpenTransactionWhereUserIsNotInitiator(otherPerson, background, currentUserChange, transactionId, trStyle) {
    $('#transactionsTable tr:last').after(
        '<tr style="' + trStyle + '">' +
        '<td style="background: ' + background + '; opacity: 0.9">' + currentUserChange + ' EUR</td>' +
        '<td>' + otherPerson + '</td>' +

        '<td style="width: 12.5%">' +
        '<form action="/api/complete_transaction" method="post">' +
        '<button type="submit" style="width: 80%" name="answer" value="accept;' + transactionId + '">Accept</button>' +
        '</form>' +
        '</td>' +

        '<td style="width: 12.5%">' +
        '<form action="/api/complete_transaction" method="post">' +
        '<button type="submit" style="width: 80%" name="answer" value="reject;' + transactionId + '">Reject</button>' +
        '</form>' +
        '</td>' +
        '</tr>'
    );
}

function renderNotOpenTransaction(otherPerson, currentUserChangeBackup, backgroundOneOne, backgroundTwoOne,
                                                      currentUserChange, transactionId, trStyle) {
    if(currentUserChangeBackup < 0) {
        $('#transactionsTable tr:last').after(
            '<tr style="' + trStyle + '">' +
            '<td style="background: ' + backgroundOneOne + '; opacity: 0.9">' + currentUserChange + ' EUR</td>' +
            '<td>' + otherPerson + '</td>' +
            '<td style="width: 12.5%"></td>' +
            '<td style="width: 12.5%"></td>' +
            '</tr>'
        );
    } else {
        $('#transactionsTable tr:last').after(
            '<tr style="' + trStyle + '">' +
            '<td style="background: ' + backgroundTwoOne + '; opacity: 0.9">' + currentUserChange + ' EUR</td>' +
            '<td>' + otherPerson + '</td>' +
            '<td style="width: 12.5%"></td>' +
            '<td style="width: 12.5%"></td>' +
            '</tr>'
        );
    }
}