# reCAPTCHA Clicker

Live site: http://habs.sdf.org/recaptcha/

required changes: 
* update DB information to a valid MySQL databse
* enable Python CGI scripting with MySQLdb
* update Google reCAPTCHA secret in POST request to a valid secret from google.com

database table structure:
* name: captcha_users
* columns: name varchar(64) primary key, pass varchar(64), captchas int default 0, youtube varchar(11) default 'oHg5SJYRHA0'
