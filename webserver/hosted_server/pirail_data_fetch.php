<?php

function thin_acc_z($obj) {
    if ($obj->{'class'} == "ATT") {
        $new_obj = array(
            'class' => $obj->{'class'},
            'time' => $obj->{'time'},
            'mileage' => $obj->{'mileage'},
            'acc_z' => $obj->{'acc_z'}
        );
        return $new_obj;
    }
    return $obj;
}

// make session read-only
session_start();
session_write_close();

// disable default disconnect checks
ignore_user_abort(true);

// set headers for stream
header("Content-Type: text/event-stream");
header("Cache-Control: no-cache");
header("Access-Control-Allow-Origin: *");

chdir("data") or die("Unable to change directory");

$myfile = fopen($_GET["file"], "r") or die("Unable to open file!");

// start stream
$count = 0;
while(!feof($myfile) && $count < 1000000){
    $line = fgets($myfile);
    if ($line != "") {
        $obj = json_decode($line);
        if ($obj->{'class'} == $_GET["classes"] && $obj->{'mileage'} >= floatval($_GET["start-mileage"]) && $obj->{'mileage'} <= floatval($_GET["end-mileage"])) {
            if ( $_GET['xform'] == "thin" ) {
                $line = json_encode(thin_acc_z($obj));
            }
            echo "event: pirail\n";
            echo "data: ".$line."\n\n";
            ob_flush();
            flush();
            $count++;
        }
    }
}
echo "event: pirail\n";
echo "data: {\"done\": true}\n\n";
ob_flush();
flush();
?>
