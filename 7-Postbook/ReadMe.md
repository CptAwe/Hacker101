# Postbook

7 flags, wow...

Private and public posts, maybe an admin page, sign in and sign up forms. Yeah, I can see why there would be so many flags.

Clicking on `Home` we get forwarded to `index.php`. So is this going to be another php roasting? Good thing we have the payload from before.

## Flag 0 - Lame even for teaching purposes

The source code doesn't tell much. Let's see the sign in page. I will enter the simple SQL command `" OR 1=1` and see what comes up:
`You've entered a wrong username/password combination. Please do not hack our system because it is insanely illegal. We will report you to PETA if you continue. Nothing is logged, but we ask you kindly not to try anything malicious.`

Hahahaaha!

Ok let's sign up then.

` Please only use fake and temporary credentials. All of the information stored is this system is considered to be open to everyone.`

What???? Ok this is the worst thing a website can say.

`Usernames should be lowercase characters only.`

No, scratch that... This is worse... Why? Why lowercase? Let's take a look at the source:

```html
[...]

<script>
    function validate() {
        var username = document.getElementById('username');
        var submit = document.getElementById('submit');

        if(/^[a-z]+$/.test(username.value)) {
            submit.disabled = false;
        } else {
            submit.disabled = true;
        }
    }
</script>

[...]
```

Ok, simple javascript to check if the username (not the password) input is lowercase.I think we can bypass this easily by editing the HTML directly.

Yes, deleting `disabled=""` enables the button after you type the credentials. the sign up was done with:

```
username: ' OR 1=1
password: asdf
```

And the sign in was successful. Ok, that's good. From the settings tab I can even change the username and the password.



I see one post from user `user`. Let's try to login as him with:

```
username: user
password: password
```

Aaaand it works... And we see the flag. That was a little lame...

The user has no private posts as far as I can see. So let's attack the admin user.

---

## Flag 1 - if 'c' is for user then 'b' is for admin!

You can change the password from settings. The request that does that is:

```
/index.php?page=account.php?username=user&password=password

HTTP/2 200 OK
date: Thu, 31 Mar 2022 14:21:38 GMT
content-type: text/html
content-length: 612
server: openresty/1.19.9.1
x-powered-by: PHP/5.5.9-1ubuntu4.24
vary: Accept-Encoding
content-encoding: gzip
X-Firefox-Spdy: h2
```

It passes both the username and the password. I can see that I have some session cookie, but I don't think it is necessary.

Let's change the password for the admin user by passing:

```
username=admin&password=password
```

It returned `200`. Let's login. Done! The flag is on the admin's home page.

That was easy!

Wait... `Flag already claimed`??? Did I change the username of the user `user`? It seems so... Ok, now there are two admins. I change the username back so that I won't confuse myself later.

I see that the link for a user's profile is:
```
/index.php?page=profile.php&id=c
```

The `id`'s value is interesting. `c` is for the user `user`, who has `id = a`? An account with no username. Ok, who has `id = b` then? `admin`!

The admin has a secret diary. I shouldn't read it, it probably contains a honeypot. Nah.... Let's read it!!!

Found the 2nd flag!

---

## Flag 2 - Again with the comments on the source code...

I don't seem to be able to change any setting for the admin. As soon as I leave profile page I get treated as a `user`. This must be happening because of the cookie.

Could I poison the cookie?

*record scratch*

Hold it. Let's look at the hints.

`You should definitely use "Inspect Element" on the form when creating a new post`

Ok, let's do this.

```html
[...]

<h2>New post</h2>

<form method="post" action="index.php?page=create.php">
  Title:<br />
  <input type="text" name="title" style="width: 250px;" required />
  <br />
  Post:<br/ >
  <textarea name="body" style="width: 250px; height: 250px;" required></textarea>
  <br /><br />
  <input type="checkbox" name="private" />Yes, this is for my own eyes only!
  <input type="hidden" name="user_id" value="4" /><!-- !!!! -->
  <br />
  <input type="submit" value="Create post" />
</form>

[...]
```

Let's reveal the input by deleting the `type="hidden"` attribute.

Now we can post from any account we want. Let's try `id=1`.

Found another flag. A little lame once again...


---

## Flag 3 - Can you do simple math though?


Let's start by looking at the hints first.

```markdown
* 189 * 5
```

Ok, cryptic, I like it!

What do I do with it though?

*Some googling later*

Ok, you are kidding me? How should I have figured this one out? `189 * 5 = 945` which is the id of a *special* post that only contains a flag.

So you go to `/index.php?page=view.php&id=945` and find the flag. Lame.

---

## Flag 4 - The id is the only vulnerability

```markdown
* You can edit your own posts, what about someone else's?
```

We have found a way to [post from any account](##-Flag-2---Again-with-the-comments-on-the-source-code...). Is the editing ability determined by the cookie? Let's see the source code first.

The `edit` button for a post that you own sends you to `/index.php?page=edit.php&id=3`. Going to this link and changing the id you can edit any post. Doing so and saving it grants you the flag.

Same *vulnerability* as the rest of the flags. Lame.

---

## Flag 5 - Not exactly cookie forgery but close enough I guess...

```markdown
* The cookie allows you to stay signed in. Can you figure out how they work so you can sign in to user with ID 1?
```

Finally, I was waiting for this. We are going to forge a cookie!

Our `id` is `3` and our cookie is `eccbc87e4b5ce2fe28308fd9f2a7baf3`.

Is the cookie bas64 of something? N0...
Is it HEX code for something? NO...

Let's paste it in google as is. It says it is MD5 and can be decrypted to `3`! Cool, can we find the MD5 hash for `id = 1`?

Yes, and it is `c4ca4238a0b923820dcc509a6f75849b`. We replace our own cookie with this one and we are the admin.

Going to the `Settings` tab we can see the password (by looking at the source code) of the admin which is `@9(a(QuDHwJq3[@2EDU2%K,j*Af]p8wZV]f`.

And now we can sign in as the admin!

In the `Home` tab is the flag. This one was a little more interesting because I haven't done anything with MD5 hashes before.


---

## Flag 6 - 

```markdown
* Deleting a post seems to take an ID that is not a number. Can you figure out what it is?
```

Indeed, going to a post that I (the current user) created we see the `delete` button redirects to `index.php?page=delete.php&id=1679091c5a880faf6fb5e6087eb1b2dc`

Seriously? Again with MD5? I just did that in the previous flag...

`1679091c5a880faf6fb5e6087eb1b2dc` is the MD5 hash for `6`. Let's delete the post for [flag #3](##-Flag-3---Can-you-do-simple-math-though?). The id for that post was `945` and its MD5 hash is `4b6538a44a1dfdc2b83477cd76dee98e`. So we go to `index.php?page=delete.php&id=4b6538a44a1dfdc2b83477cd76dee98e`. It says `Post not found`. Shame...

Let's try another post that we don't own.

And when we delete it we get the flag.

---

Done. Not as fun as the others.

