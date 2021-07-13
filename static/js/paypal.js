var CREATE_PAYMENT_URL  = 'http://127.0.0.1:5000/api/payment';
var EXECUTE_PAYMENT_URL = 'http://127.0.0.1:5000/api/execute';

paypal.Button.render({
    env: 'sandbox', // Or 'sandbox'
    commit: true, // Show a 'Pay Now' button

    // payment: function() {
    //     return paypal.request({method: "post", url: CREATE_PAYMENT_URL, json: { "amount": $("#amount").val()}})
    //         .then(function(data) {
    //             return data.paymentID;
    //         });
    // },

    payment: function() {
        return paypal.request.post(CREATE_PAYMENT_URL, [$("#amount").val()]).then(function(data) {
            return data.paymentID;
        });
    },

    onAuthorize: function(data) {
        return paypal.request.post(EXECUTE_PAYMENT_URL, {
            paymentID: data.paymentID,
            payerID:   data.payerID
        }).then(function() {
            $("#paypal-button").remove();
            $("#amountDiv").remove();
            $("body").append('<p>Purchase completed.</p>').append('<a href="/h">Go back</a>')
        });
    }
}, '#paypal-button');