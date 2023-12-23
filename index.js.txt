const express = require('express');
const axios = require('axios');
const uuid = require('uuid');
const totp = require('totp-generator');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Hello 👋 thank you for using my Token Getter API PM ME ON SHIKI').end();
});

app.get('/login', async (req, res) => {
  const { email, password } = req.query;

  try {
    const deviceID = uuid.v4();
    const adid = uuid.v4();

    function randomString(length) {
      const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
      let result = characters.charAt(Math.floor(Math.random() * characters.length));

      for (let i = 0; i < length - 1; i++) {
        result += characters.charAt(Math.floor(36 * Math.random()));
      }

      return result;
    }

    function encodeSig(string) {
      const sortedData = Object.keys(string)
        .sort()
        .reduce((result, key) => {
          result[key] = string[key];
          return result;
        }, {});

      let data = '';
      for (const info in sortedData) {
        data += info + '=' + sortedData[info];
      }
      data = md5(data + '62f8ce9f74b12f84c123cc23437a4a32');
      return data;
    }

    function md5(string) {
      return require('crypto')
        .createHash('md5')
        .update(string)
        .digest('hex');
    }

    const form = {
      adid: adid,
      email: email,
      password: password,
      format: 'json',
      device_id: deviceID,
      cpl: 'true',
      family_device_id: deviceID,
      locale: 'en_US',
      client_country_code: 'US',
      credentials_type: 'device_based_login_password',
      generate_session_cookies: '1',
      generate_analytics_claim: '1',
      generate_machine_id: '1',
      currently_logged_in_userid: '0',
      irisSeqID: 1,
      try_num: '1',
      enroll_misauth: 'false',
      meta_inf_fbmeta: 'NO_FILE',
      source: 'login',
      machine_id: randomString(24),
      fb_api_req_friendly_name: 'authenticate',
      fb_api_caller_class: 'com.facebook.account.login.protocol.Fb4aAuthHandler',
      api_key: '882a8490361da98702bf97a021ddc14d',
      access_token: '350685531728%7C62f8ce9f74b12f84c123cc23437a4a32',
    };

    form.sig = encodeSig(form);

    const options = {
      url: 'https://b-graph.facebook.com/auth/login',
      method: 'post',
      data: form,
      transformRequest: [
        (data, headers) => {
          return require('querystring').stringify(data);
        },
      ],
      headers: {
        'content-type': 'application/x-www-form-urlencoded',
        'x-fb-friendly-name': form['fb_api_req_friendly_name'],
        'x-fb-http-engine': 'Liger',
        'user-agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
      },
    };

    return new Promise((resolve) => {
      axios
        .request(options)
        .then(async (response) => {
          try {
            response.data.access_token_eaad6v7 = await convertToken(
              response.data.access_token
            );
            response.data.cookies = await convertCookie(
              response.data.session_cookies
            );
            response.data.session_cookies = response.data.session_cookies.map(
              (e) => {
                return {
                  key: e.name,
                  value: e.value,
                  domain: 'facebook.com',
                  path: e.path,
                  hostOnly: false,
                };
              }
            );

            return res.json({
              status: true,
              message: 'Retrieve information successfully!',
              data: response.data,
            });
          } catch (e) {
            return res.json({
              status: false,
              message: 'Please enable 2FA authentication and try again!',
            });
          }
        })
        .catch((error) => {
          if (error.response.data.error.code == 401) {
            return res.json({
              status: false,
              message: error.response.data.error.message,
            });
          }

          if (twofactor == '0' && (!_2fa || _2fa == '0')) {
            return res.json({
              status: false,
              message: 'Please enter the 2-factor authentication code!',
            });
          }

          try {
            _2fa = _2fa != '0' ? _2fa : totp(decodeURI(_2fa).replace(/\s+/g, '').toLowerCase());
          } catch (e) {
            return res.json({
              status: false,
              message: 'Invalid 2-factor authentication code!',
            });
          }

          form.twofactor_code = _2fa;
          form.encrypted_msisdn = '';
          form.userid = error.response.data.error.error_data.uid;
          form.machine_id = error.response.data.error.error_data.machine_id;
          form.first_factor = error.response.data.error.error_data.login_first_factor;
          form.credentials_type = 'two_factor';
          form.sig = encodeSig(form);
          options.data = form;

          axios
            .request(options)
            .then(async (response) => {
              response.data.access_token_eaad6v7 = await convertToken(
                response.data.access_token
              );
              response.data.cookies = await convertCookie(
                response.data.session_cookies
              );
              response.data.session_cookies = response.data.session_cookies.map(
                (e) => {
                  return {
                    key: e.name,
                    value: e.value,
                    domain: 'facebook.com',
                    path: e.path,
                    hostOnly: false,
                  };
                }
              );

              return res.json({
                status: true,
                message: 'Retrieve information successfully!',
                data: response.data,
              });
            })
            .catch((error) => {
              return res.json({
                status: false,
                message: error.response.data,
              });
            });
        });
    });
  } catch (e) {
    return res.json({
      status: false,
      message: 'Please check your account and password again!',
    });
  }
});

async function convertCookie(session) {
  let cookie = '';
  for (let i = 0; i < session.length; i++) {
    cookie += session[i].name + '=' + session[i].value + '; ';
  }
  return cookie;
}

async function convertToken(token) {
  return new Promise((resolve) => {
    axios
      .get(`https://api.facebook.com/method/auth.getSessionforApp?format=json&access_token=${token}&new_app_id=275254692598279`)
      .then((response) => {
        if (response.data.error) {
          resolve();
        } else {
          resolve(response.data.access_token);
        }
      });
  });
}

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
        
