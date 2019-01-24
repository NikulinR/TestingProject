<?php

$commandString = 'start /b python.lnk C:\xampp\htdocs\Python\source\app.py';
echo "Идёт запуск сервера...\n ";
pclose(popen($commandString, 'r'));
sleep(2);
header("Location: http://127.0.0.1:5000/");

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
?>
