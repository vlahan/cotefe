<?php
session_start();

if ($_SESSION[$_SESSION["session"]]["logged"]==true) {
    session_destroy();
    $host  = $_SERVER['HTTP_HOST'];
    $extra = 'index.php';
    header("Location: http://$host/$extra");
}

?>
