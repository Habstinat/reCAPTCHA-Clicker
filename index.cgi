#!/usr/bin/env python

import os
import cgi
import cgitb; # cgitb.enable() # for troubleshooting
import cookielib
import Cookie
import requests
import MySQLdb
import json

db = MySQLdb.connect(
    host="ma.sdf.org",
    user="habs",
    passwd="password",
    db="habs")
cur = db.cursor()
form = cgi.FieldStorage()

if "register" in form:
    cur.execute("insert into captcha_users (name,pass) values (%s,%s)",(form["name"].value,form["pass"].value))
    db.commit()
if "login" in form or "register" in form:
    ident = Cookie.SimpleCookie()
    ident['captcha-name'] = form['name'].value
    ident['captcha-pass'] = form['pass'].value
    print ident
elif 'logout' in form:
    ident = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
    ident['captcha-name']['expires'] = "Thu, 01 Jan 1970 00:00:00 GMT"
    ident['captcha-name'] = ""
    ident['captcha-pass']['expires'] = "Thu, 01 Jan 1970 00:00:00 GMT"
    ident['captcha-pass'] = ""
    print ident

print "Content-type: text/html"
print

if 'register' in form or 'login' in form or 'logout' in form:
    print "<meta http-equiv='refresh' content='0'/>"

print """
<html>
<head><title>reCAPTCHA Clicker</title></head>
<body>
<div style="width:100%; border: thin solid black;text-align:center;">
<h1>reCAPTCHA Clicker</h1>
<p><i>Now with fixed YouTube IDs</i></p>
<p style='font-size:70%;'>Problem? <a href="http://habs.sdf.org/recaptcha/">Click here</a> to refresh</small>
<div style="float:left;width:40%;border:thin solid black;text-align:center;">
"""

cookied = False
if 'HTTP_COOKIE' in os.environ:
    ident = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
    cur.execute("select pass from captcha_users where name = %s",ident['captcha-name'].value)
    try:
        passw = cur.fetchone()[0]
    except:
        passw = None
    cookied = True
if cookied == True and passw == ident['captcha-pass'].value:
    #print "<p>Authenticated successfully</p>"
    if 'youtube' in form:
        cur.execute("update captcha_users set youtube = %s where name = %s",(form['videoid'].value,ident['captcha-name'].value))
        db.commit()
    cur.execute("select captchas from captcha_users where name = %s",ident['captcha-name'].value)
    captchas = cur.fetchone()[0]
    if "captcha" in form:
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data={'secret':'secret','response':form['g-recaptcha-response'].value})
        if r.json()['success'] == True:
            captchas = captchas + 1
            cur.execute("update captcha_users set captchas = %s where name = %s",(captchas,ident['captcha-name'].value))
            db.commit()
        #else: print "<p><i>Incorrect captcha!</i></p>"
    print "<p>User <b>%s</b> has <b>%d</b> reCAPTCHAs today</p>" % (cgi.escape(ident['captcha-name'].value),captchas)
    print """
    <form method="post" action="index.cgi">
    <script src='https://www.google.com/recaptcha/api.js'></script>
    <div style="display:block;width:304px;margin:0 auto;">
    <div class="g-recaptcha" data-sitekey="6LerRCUTAAAAABnPnU1vr0btSKsHmx_bRxPPNpre"></div>
    </div>
    <p><input type="submit" name="captcha" value="Submit reCAPTCHA"/></p>
    <p>11-character YouTube video ID (to choose a featured video when you become the daily leader):</p>
    <p>For example: If the orginal YouTube URL is <i>https://youtube.com/watch?v=oHg5SJYRHA0</i>, the video ID is <b>oHg5SJYRHA0</b></p>
    <p><input type="text" name="videoid" value=""/>
    <input type="submit" name="youtube" value="Set My YouTube Video ID"/></p>
    """
    cur.execute("select youtube from captcha_users where name = %s",ident['captcha-name'].value)
    videoid = cur.fetchone()[0]
    print """
    <p>Your current Video ID is <b>%s</b></p>
    <p><input type="submit" name="logout" value="Log out"/></p>
    </form>
    """ % cgi.escape(videoid)
else:
    print """
    <form method="post" action="index.cgi">
    <p>username: <input type="text" name="name"/></p>
    <p>password: <input type="password" name="pass"/></p>
    <p><input type="submit" name="login" value="Log in"/> OR <input type="submit" name="register" value="Register"/></p>
    <p><i>(there is no separate &quot;register&quot; page -- just fill out the two fields and click &quot;Register&quot; to get started!)</i></p>
    </form>
    """

print "</div><div style='float:right;width:40%;border:thin solid black;text-align:center;'>"
cur.execute("select captchas,name,youtube from captcha_users")
names = cur.fetchall()
leaderboard = sorted(names,key=lambda tup: tup[0],reverse=True)
print """<p>As the daily leader, RCC user <b>%s</b> gets to choose the current featured YouTube video:</p>
<iframe width="420" height="315" src="https://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>""" % (cgi.escape(leaderboard[0][1]),cgi.escape(leaderboard[0][2]))
print """<p>Daily leaders:</p>
<table border="1" align="center">
<tr><td>Ranking</td><td>User</td><td>CAPTCHAs</td></tr>"""
rank = 1
for leader in leaderboard[:10]:
    print "<tr><td>" + str(rank) + "</td><td><a href='https://youtube.com/watch?v=" + cgi.escape(leader[2]) + "'>" + cgi.escape(leader[1]) + "</a></td><td>" + str(leader[0]) + "</td></tr>"
    rank = rank + 1
print "</table><br /></div>"
print "</div>"
print """
<a href='mailto:habs+captcha@sdf.org'>contact</a> | <a href='https://www.reddit.com/r/incremental_games/comments/4tj11b/recaptcha_clicker_the_only_cheatproof_incremental/'>reddit</a>
</p>
"""
db.close()


