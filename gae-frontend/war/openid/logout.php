<?php
    session_start();
    session_destroy();
    //unset$_SESSION[$_SESSION["session"]]()
    $host  = $_SERVER['HTTP_HOST'];
    $extra = 'index.php';
    header("Location: http://$host/$extra");
?>