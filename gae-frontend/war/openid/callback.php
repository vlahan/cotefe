<?php
ob_start();

$valid_identifiers = array(
    "http://claudiodonzelli.myopenid.com/", // claudiodonzelli.myopenid.com
    "https://www.google.com/profiles/110662023037380294102", // solenoidd@gmail.com
    "https://www.google.com/profiles/103269797818246441292", // donzelli@cotefe.net
    "https://www.google.com/profiles/101901861915259369647", // vlahan@cotefe.net
    );

$rpx_api_key = '726651f55a8c05d5adc230edba6a253c30276b99';
$token = $_POST['token'];

//echo "SERVER VARIABLES:\n";
//var_dump($_SERVER);
//echo "HTTP POST ARRAY:\n";
//var_dump($_POST);

if(strlen($token) == 40) {

  $post_data = array('token'  => $token,
                     'apiKey' => $rpx_api_key,
                     'format' => 'json',
                     'extended' => 'true');

  $curl = curl_init();
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($curl, CURLOPT_URL, 'http://rpxnow.com/api/v2/auth_info');
  curl_setopt($curl, CURLOPT_POST, true);
  curl_setopt($curl, CURLOPT_POSTFIELDS, $post_data);
  curl_setopt($curl, CURLOPT_HEADER, false);
  curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
  curl_setopt($curl, CURLOPT_FAILONERROR, true);
  $result = curl_exec($curl);
  if ($result == false){
    echo "\n".'Curl error: ' . curl_error($curl);
    echo "\n".'HTTP code: ' . curl_errno($curl);
    echo "\n"; var_dump($post_data);
  }
  curl_close($curl);
  
  $auth_info = json_decode($result, true);

  if ($auth_info['stat'] == 'ok') {
    //echo "\n auth_info:";
    //echo "\n"; var_dump($auth_info);
    
        if (in_array($auth_info["identifier"], $valid_identifiers))
        {
    
            session_start();
    
            $host  = $_SERVER['HTTP_HOST'];
            $extra = 'dashboard.php';
            $_SESSION["session"]=session_id();
            $_SESSION[$_SESSION["session"]]["logged"]=1;			
            $_SESSION[$_SESSION["session"]]["identifier"]=$auth_info["identifier"];
            $_SESSION[$_SESSION["session"]]["name"]=$auth_info["name"]["formatted"];
            $_SESSION[$_SESSION["session"]]["email"]=$auth_info["email"];
            header("Location: http://$host/$extra");
        }
    }

    } else {
      echo "\n".'An error occured: ' . $auth_info['err']['msg']."\n";
      var_dump($auth_info);
      echo "\n";
      var_dump($result);
      $host  = $_SERVER['HTTP_HOST'];
      $extra = 'index.php';
      header("Location: http://$host/$extra");
    }
}else{
  
  echo 'Authentication canceled.';
  $host  = $_SERVER['HTTP_HOST'];
  $extra = 'index.php';
  header("Location: http://$host/$extra");
}
$debug_out = ob_get_contents();
ob_end_clean();
?>
<html>
<head>
<title>Powered by Janrain Engage</title>
</head>
<body>
<!-- content -->
<pre>
<?php echo $debug_out; ?>
</pre>
<!-- javascript -->
</body>
</html>