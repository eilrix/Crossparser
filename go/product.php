<?php

$prod_id_link = $_GET["id"];

$return_link = 'no link found';
$file_txt = '';

if (isset($prod_id_link))
{
    $filename = '/var/www/html/boots-market/crossparser/data/partner_links';
    $myfile = fopen($filename, "r") or die("Unable to open file!");
    $file_txt = fread($myfile,filesize($filename));
    fclose($myfile);

    $links_arr = explode("\n", $file_txt);

    $links_parsed_arr = array();

    foreach ($links_arr as $links)
    {
        $links_line = explode("$$", $links);
        $links_parsed_arr[] = array( $links_line[0] => $links_line[1]);
    }

    foreach ($links_parsed_arr as $links)
    {
        //echo $links[$prod_id_link];

        if (array_key_exists($prod_id_link, $links))
        {
            $return_link = $links[$prod_id_link];
        }
    }

}

//echo $return_link;

$html = '
<head>
<title>User Info</title>
<meta name="robots" content="noindex, nofollow" />
</head>
<body>
<p id="redirect">Wait</p>

<script>
var link = "' . $return_link . '";

if (link == "no link found") {
    document.getElementById("redirect").innerText = "No link found";
}
else {
    document.getElementById("redirect").innerText = "Redirecting...";
    window.location.href = link;
}

</script>

</body>';

echo $html;

