import React from 'react';
import Cookies from 'universal-cookie';
import axios from 'axios';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoggedIn: false,
      specs: {}
    };
    this.getSpecs = this.getSpecs.bind(this);
    this.authenticateUser = this.authenticateUser.bind(this);
  }
  getSpecs() {
    const request = axios({
      method: 'GET',
      url: window.location.protocol + "//" + window.location.hostname + window.location.pathname + "api/specs/"
    });
    request.then(
      response => {
        this.setState({specs: response.data});
      },
    );
  }
  authenticateUser() {
    const cookies = new Cookies();
    var columbus_token = cookies.get('fg_token');
    if (columbus_token !== undefined) {
      var auth_header = 'Bearer ' + cookies.get('fg_token');
      const request = axios({
        method: 'GET',
        url: "https://api.cdrive.columbusecosystem.com/user-details/",
        headers: {'Authorization': auth_header}
      });
      request.then(
        response => {
          this.setState({isLoggedIn: true});
        }, err => {
          cookies.remove('fg_token');
          this.authenticateUser();
        }
      );
      return(null);
    }
    var url_string = window.location.href;
    var url = new URL(url_string);
    var code = url.searchParams.get("code");
    var redirect_uri = this.state.specs.cdriveUrl + "app/" + this.state.specs.username + "/feature-gen/";
    if (code == null) {
      window.location.href = this.state.specs.authUrl + "o/authorize/?response_type=code&client_id=" + this.state.specs.clientId + "&redirect_uri=" + redirect_uri + "&state=1234xyz";
    } else {
      const request = axios({
        method: 'POST',
        url: redirect_uri + "api/authentication-token/",
        data: {
          code: code,
          redirect_uri: redirect_uri
        }
      });
      request.then(
        response => {
          cookies.set('fg_token', response.data.access_token);
          this.setState({isLoggedIn: true});
        },
        err => {
        }
      );
    }
  }
  render() {
    if (Object.keys(this.state.specs).length === 0) {
      this.getSpecs();
      return(null);
    } else if (!this.state.isLoggedIn) {
      this.authenticateUser();
      return(null);
    } else {
      return (
        <div>
          Successfully authenticated user!
        </div>
      );
    }
  }
}

export default App;
