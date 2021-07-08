function renderProfile(userId) {
    // clear main and render the form
    $("#main").empty().append('<form id="updateProfileForm" action="/h/settings" method="post"></form>');
    $("#updateProfileForm").append('<h2>E-mail</h2>')
        .append('<input type="text" name="new_email" placeholder="Enter new e-mail..." required>')
        .append('<h2>New password</h2>')
        .append('<input type="password" name="new_pass" placeholder="Enter new password..." required>')
        .append('<br><br><input type="hidden" name="action" value="update profile">')
        .append('<input type="hidden" name="user_id" value=' + userId + '>')
        .append('<input type="submit" value="Done">');
}