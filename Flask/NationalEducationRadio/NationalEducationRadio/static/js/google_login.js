/**
 * Created by Jessie on 2018/03/20
 */


function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.

    $.ajax({
        type: 'POST',
        url: '/radio/API_GOOGLE_login',
        data: JSON.stringify({
            'userID' : profile.getId(),
            'userName' : profile.getName(),
            'userEmail' : profile.getEmail()
        }),
        contentType: "application/json; charset=utf-8",
    }).done(function() {
        signOut();
        window.location.replace('.')
    });
    
  }

  function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
      console.log('User signed out.');
    });
  }