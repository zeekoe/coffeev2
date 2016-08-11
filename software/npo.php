<?php
/*
$opts = array('http' => array(
	'method' => "GET",
	'header' => "Host: l2cm5e20e20eac00574843a4000000.571d3ac5d842e4e5.kpnsmoote1e.npostreaming.nl
User-Agent: VLC/2.2.1 LibVLC/2.2.1
Range: bytes=0-
Connection: close
Icy-MetaData: 1
",'timeout' => 300));
$context = stream_context_create($opts);  
$tvurl = "http://l2cm5e20e20eac00574843a4000000.571d3ac5d842e4e5.kpnsmoote1e.npostreaming.nl/d/live/npo/tvlive/ned2/ned2.isml/ned2-audio=128000-video=700000-4931.ts";
$dummy = file_get_contents($tvurl, false, $context);
var_dump($dummy === false);
exit;
*/
	$kanaal = intval($_GET['kanaal']);
	if($kanaal < 1 or $kanaal > 3)
		die('kies kanaal');
	$response = implode('',file("http://ida.omroep.nl/npoplayer/i.js?s=http://www.npo.nl/live/npo-" . $kanaal));
	if($response === NULL)
		die('fout1');
	preg_match('/token = "([a-zA-Z0-9]*)"/', $response, $matches);
	$token = $matches[1];
	//print "Complete response: " . $response . "<br>";
	//print "Token opgehaald: <br>" . $token . "<br>";
	$token = friemelToken($token);
	
	#url = "probeer url: " + "http://ida.omroep.nl/aapi/?callback=jQuery18308831475791569496_1428082441201&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned"+channel+"/ned"+channel+".isml/ned"+channel+"-audio=128000-video=700000.m3u8&token=%s&version=4.0" % (token)
	# GET /aapi/?callback=jQuery18306757661136888681_1440684352682&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned1/ned1.isml/ned1.m3u8&token=8i0n188o7l6cgibiub22s422r3&version=5.1.0&_=1440684354971 HTTP/1.1\r\n
	
	$url = "http://ida.omroep.nl/aapi/?callback=jQuery18306757661136888681_1440684352682&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned".$kanaal."/ned".$kanaal.".isml/ned".$kanaal.".m3u8&token=".$token."&version=5.1.0&_=" . ( date('U') * 1000 - 3504);

	#url = "http://ida.omroep.nl/aapi/?callback=jQuery18306757661136888681_1440684352682&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned"+channel+"/ned"+channel+".isml/ned"+channel+"-audio=128000-video=700000.m3u8&token=%s&version=5.1.0&_=%d"
	//print "probeer url: ". $url."\n";
	$response = implode('',file($url));
	if($response === NULL)
		die('fout3');
	//echo $response."\n";
	preg_match('/"stream":"(http.*?)"}/', $response, $matches2);
	$newurl = str_replace('\\/','/',$matches2[1]);
	//print "Stream pre-url: " . $newurl ."\n";

	$response = implode('',file($newurl));
	if($response === NULL)
		die('fout4');
	#response = 'setSource("http:\/\/l2cmde7ca8fc9a00551ed257000000.e0e5ecb0e1884f37.kpnsmoote1a.npostreaming.nl\/d\/live\/npo\/tvlive\/ned2\/ned2.isml\/ned2.m3u8")'
	preg_match('/setSource\("(http.*?)"\)/', $response, $matches3);
	$url = str_replace('\\/','/',$matches3[1]);
	$url = str_replace('ned' . $kanaal . '.m3u8', 'ned' . $kanaal . '-audio=128000-video=700000.m3u8',$url);
	//print "Stream url: " . $url."\n";

	preg_match('/http:\/\/.*?\.nl/', $url,$matches4);
	$url_base = $matches4[0];
	print "Stream url: " . $url_base."\n";


$opts = array('http' => array(
	'method' => "GET",
	'header' => "Host: ".substr($url_base,7)."
User-Agent: VLC/2.2.1 LibVLC/2.2.1
Range: bytes=0-
Connection: close
Icy-MetaData: 1
",'timeout' => 300));
$context = stream_context_create($opts);  
//	echo '<pre>';
//	var_dump($opts);

	$tv = $kanaal;
	
	$tvdata = array();
	
	while(1) {
		$f = file($url);
		foreach($f as $r) {
			//$f = file('/tmp/tv'); 
			if(substr($r,0,1) != '#') {
				$tvurl = trim($url_base."/d/live/npo/tvlive/ned".$tv."/ned".$tv.".isml/" . $r);
				//$ch = curl_init($url);
				//curl_setopt($ch, CURLOPT_HTTPHEADER, $headers); 
				if(array_key_exists($r,$tvdata)) {
//					echo "sleeping\n";
					sleep(5);
				}
				else {
					$dummy = file_get_contents($tvurl, false, $context);
					echo $dummy;
//					echo "vlc \"".$tvurl."\"\n";
					$tvdata[$r] = 1;
				}
				flush();
				//var_dump($dummy);
				//$h = fopen('/tmp/fifo.mp4','w');
				//echo "schrijf\n";
				//fwrite($h,file_get_contents($url, false, $context));
				//echo "geschreven\n";
			}
		}
	}

function friemelToken($token) {
	$token1 = substr($token,0,5);
	$token2 = substr($token,5,21-5);
	$token3 = substr($token,21);
	$n = 0;
	$a = 0;
	$b = 0;
	$res = '';
	for($i = 0; $i < strlen($token2); $i++) {
		$c = substr($token2,$i,1);
		$g = -1;
		$g = intval($c);
		if($c != '0' && $g == 0) $g = -1;
		if ($g > -1) {
			$n = $n + 1;
			if ($n == 1)
				$a = $i;
			if ($n == 2)
				$b = $i;
		}
		if ($n > 1 ) {
//			print $a .'-'.$b.'<br>';
			$g1 = substr($token2,$a,1);
			$res = $token1 . substr($token2,0,$a) . substr($token2,$b,1) . substr($token2,$a+1,$b-$a-1) . substr($token2,$a,1) . substr($token2,$b+1) . $token3;
			break;
		}
	}
	if($n < 2) {
		$a = 12-5;
		$b = 13-5;
		$g1 = substr($token2,$a,1);
		$res = $token1 . substr($token2,0,$a) . substr($token2,$b,1) . substr($token2,$a+1,$b-$a-1) . substr($token2,$a,1) . substr($token2,$b+1) . $token3;
	}
//	print $res;
	return $res;
}
?>