// activation-script.js

// Function to parse URL parameters
function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

// Get uid and token from the current URL
const uid = getParameterByName('uid');
const token = getParameterByName('token');

// Output for testing (you can remove this in production)
console.log('UID:', uid);
console.log('Token:', token);

// Function to activate account using Axios with custom headers
const activateAccount = (uid, token) => {
  const activationEndpoint = 'http://127.0.0.1:8000/auth/users/activation/';

  // Data to be sent in the POST request
  const data = {
      uid: uid,
      token: token,
  };

  // Custom headers
  const headers = {
    'Content-Type': 'application/json',  // Adjust the content type as needed
  };

  // Sending the POST request using Axios with custom headers
  axios.post(activationEndpoint, data, { headers })
      .then(response => {
          // Handle successful activation
          console.log('Activation successful', response.data);
      })
      .catch(error => {
          // Handle activation error
          console.error('Activation error', error);
      });
};

// Call the activateAccount function
activateAccount(uid, token);
