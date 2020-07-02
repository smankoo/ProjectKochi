$(function () {
    $('a#download').bind('click', function () {
        // $("input#url").val("https://music.youtube.com/playlist?list=OLAK5uy_m_Kjhx3wck_RmcJuPf0kLR60t4hpP65Pc");
        url = $("input#url").val();
        console.log("here")
        set_button_loading();
        if (url.includes("playlist")) {
            get_playlist(url);
        } else {
            get_video(url);
        }
    });

});

function get_video(url) {

    console.log("download_clicked()")
    $("div#downloadlinkdiv").hide();


    const regex = RegExp('(http\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+');

    if (regex.test(url) == false) {
        console.log("Bad URL: " + url)
        // alert("Bad URL: " + url);
        $("#badurl-alert").fadeTo(2000, 500).slideUp(500, function () {
            $("#badurl-alert").slideUp(500);
        });
        return;;
    }

    // start_progress_bar();
    // alert(url);
    $.getJSON($SCRIPT_ROOT + '/_download', {
        "url": url
    }, function (data) {
        $currloc = window.location.href.split('?')[0].split('#')[0];
        // alert($currloc + 'getfile?downloadid=' + data.downloadid);
        $("a#downloadlink").attr("href", $currloc + 'getfile?downloadid=' + data.downloadid);
        $("div#downloadlinkdiv").show();
        $('.progress-bar-label').text("Done");
        set_button_normal();
        window.location.href = $currloc + 'getfile?downloadid=' + data.downloadid
    });

    $.get($SCRIPT_ROOT + '/cleanup')

    return false;
}

function get_playlist(url) {
    console.log("fired")
    console.log("url: " + url);


    $("#playlisttable tr").slice(1).remove();

    // // alert("url: " + url)
    $.getJSON($SCRIPT_ROOT + '/_getplaylistitems', {
        "url": url
    }, function (ydl_info) {
        console.log(ydl_info);
        $("#playlisttitle").text(ydl_info['title']);
        $("#playlistdiv").show();

        entries = ydl_info['entries'];

        for (var i = 0; i < entries.length; i++) {
            var item = entries[i];

            row = "<tr>";
            col = "<td> \
                    <div class=\"form-check\"> \
                        <input class=\"form-check-input\" type=\"checkbox\" id=\"ckb" + item['playlist_index'] + "\" value=\"playlist_index" + item['playlist_index'] + " \"> \
                    </div>\
                    </td>";

            row += col;
            row += "<td>" + item['playlist_index'] + "</td>"
            row += "<td><img src=" + item['thumbnails'][0]['url'] + "></td>";
            row += "<td>" + item['title'] + "</td>"

            var durationSecs = new Date(null);
            durationSecs.setSeconds(item['duration']); // specify value of SECONDS
            var durationPretty = durationSecs.toISOString().substr(11, 8);

            var hr = durationPretty.substring(0, 3);
            if (hr == "00:") {
                durationPretty = durationPretty.substring(3);
            }

            row += "<td>" + durationPretty + "</td>";
            row += "</tr>";

            $('#playlisttable').append(row);

        }

        set_button_normal();

    });

    console.log("fired2")
}

function isHidden(el) {
    return (el.offsetParent === null)
}

// function start_progress_bar() {
//   $("#progressdiv").show();
//   var source = new EventSource("/_progress");
//   source.onmessage = function (event) {
//     $('.progress-bar').css('width', event.data + '%').attr('aria-valuenow', event.data);
//     $('.progress-bar-label').text(event.data + '%');

//     if (event.data == 100) {
//       source.close()
//     }
//   }
// }

function set_button_loading() {
    console.log("inside set_button_loading");
    $("span#loadingspinner").show();
    $("span#downloadbuttontext").text("Downloading...");
    $("button#downloadbutton").prop("disabled", true);
}

function set_button_normal() {
    $("span#loadingspinner").hide();
    $("span#downloadbuttontext").text("Download");
    $("button#downloadbutton").prop("disabled", false);
}

var bartimer
function start_progress_bar() {
    $('.progress-bar').css('width', 0 + '%').attr('aria-valuenow', 0);
    $('.progress-bar-label').text(0 + '%');
    $("#progressdiv").show();
    bartimer = setInterval(update_progress_bar, 100);
}

function update_progress_bar() {
    $.getJSON('/_getprogress', {}, function (data) {
        // alert(data.perc)
        $('.progress-bar').css('width', data.perc + '%').attr('aria-valuenow', data.perc);
        $('.progress-bar-label').text(data.perc + '%');
        if (data.perc == 100) {
            clearInterval(bartimer)
            $('.progress-bar-label').text('Download complete. Now converting...');
            $("span#downloadbuttontext").text("Converting...");
        }
    });

}

function show_playlist() {
    $("#playlistdiv").show();
}
