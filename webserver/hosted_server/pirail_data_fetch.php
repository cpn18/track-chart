<?php

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

	$count = 0;
        // start stream
	while(!feof($myfile) && $count < 1000000){
		$line = fgets($myfile);
		if ($line != "") {
                  $obj = json_decode($line);
		  if ($obj->{'class'} == $_GET["classes"] && $obj->{'mileage'} >= floatval($_GET["start-mileage"]) && $obj->{'mileage'} <= floatval($_GET["end-mileage"])) {
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
