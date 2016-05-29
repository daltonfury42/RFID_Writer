<?php

error_reporting(E_ERROR | E_PARSE);

$ReaderIp="192.168.1.201";

$port=100;
$timeout = "30";

//Data for writing
$data=$_REQUEST['data'];


/* Create a TCP/IP socket. */
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    echo "socket_create() failed: reason: " . socket_strerror(socket_last_error()) . "\n";
} else {
    //echo "OK.\n";
}

//echo "Attempting to connect to '$ReaderIp' on port '$port'...";
$result = @socket_connect($socket, $ReaderIp, $port);
if ($result === false) {
    echo "socket_connect() failed.\nReason: ($result) " . socket_strerror(socket_last_error($socket)) . "\n";
} else {
   // echo "OK.\n";
}

//$epc="";
$l=strlen($data);
for($j=0;$j<$l;$j++)
{
	$epc[]= ord(substr($data,$j,1));
}

for($j=0;$j<12-$l;$j++)
{
	$epc[]= 0;
}

//echo $epc."<br>";

$addr=7;
$fail=0;
$succ=0;

for($j=0;$j<6;$j++)
{
$b2=intval($epc[$j*2]);
$b1=intval($epc[$j*2+1]);

//echo $addr+j .",".$b1.",".$b2."<br>";
//echo "Sending Write request... <br>";    10,255,10,137,0,0,0,0,1,3,53,53,246

$cmd = chr(10) . chr(255) . chr(10) . chr(137) .chr(0).chr(0).chr(0).chr(0).chr(1).chr($addr-$j).chr($b1).chr($b2). chr(CheckDigit($addr-$j,$b1,$b2)) ;
//$cmd = chr(10) . chr(255) . chr(05) . chr(129) .chr($addr-$j).chr($b1).chr($b2). chr(246) ;
//echo $cmd . "<br>";

socket_write($socket, $cmd, strlen($cmd));

//echo "Reading response: <br>";

$out = socket_read($socket, 2048);
if(ord(substr($out,3,1))==82) $fail=1;

/*for($i=0;$i<strlen($out);$i++) {	
	echo ord(substr($out,$i,1))."<br>";
	}
	echo "<br>"."<br>";*/
}

//read start
//echo "Sending Read request... <br>";

$cmd = chr(10) . chr(255) . chr(2) . chr(128) . chr(117) ;
socket_write($socket, $cmd, strlen($cmd));

//echo "Reading response: <br>";
$out = socket_read($socket, 2048);
$cnt=ord(substr($out,5,1));

	//echo "Sending get tag data request... <br>";
	$cmd = chr(10) . chr(255) . chr(3) . chr(65).chr(16)  .  chr(163) ;
	socket_write($socket, $cmd, strlen($cmd));

	//echo "Reading response: <br>";
	$out="";
	$out = socket_read($socket, 2048);

	for($j=0;$j<$cnt;$j++)
	{
		$d="";
		for($i=($j*14)+7;$i<($j*14)+19;$i++) {	
			//echo ord(substr($out,$i,1))."<br>";
			if(ord(substr($out,$i,1))!=0) $d= substr($out,$i,1).$d;
		}
		if(ord(substr($d,0,1))==1) $d=substr($d,1);
		if($d==$data1) $succ=1;
			//echo "$d|$data";
	}
	//echo "Reading response: <br>";
	$out="";

//read end
if($succ) echo "Success"; 
else echo "Failed";
die();

function CheckDigit($a, $b, $c)
{
	$i=$a+$b+$c+413;
	
	if($i<255) $i= 256-$i;
	else if ($i<511) $i= 512-$i;
	else if ($i<1023) $i= 1024-$i;
	
	if ($i>255) $i=$i-256;
	
	return $i;
}

?>
