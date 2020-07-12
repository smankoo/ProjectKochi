$(function () {
    $("input#ckball").change(function () {
        if (this.checked) {
            $(".ckbplaylistitem").each(function () {
                this.checked = true;
            });
        } else {
            $(".ckbplaylistitem").each(function () {
                this.checked = false;
            });
        }
        update_playlist_download_count();
    });

    $('body').on('click', '.ckbplaylistitem', function () {

        if ($(this).is(":checked")) {
            var isAllChecked = 0;

            $(".ckbplaylistitem").each(function () {
                if (!this.checked)
                    isAllChecked = 1;
            });

            if (isAllChecked == 0) {
                $("input#ckball").prop("checked", true);
            }
        }
        else {
            $("input#ckball").prop("checked", false);
        }
        update_playlist_download_count();
    });


    $('a#download').bind('click', function () {
        // $("input#url").val("https://music.youtube.com/playlist?list=OLAK5uy_m_Kjhx3wck_RmcJuPf0kLR60t4hpP65Pc");
        $("#playlistdiv").hide();
        $("div#downloadlinkdiv").hide();

        url = $("input#url").val();
        const regex = RegExp('(http\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+');

        if (regex.test(url) == false) {
            console.log("Bad URL: " + url)
            // alert("Bad URL: " + url);
            $("#badurl-alert").fadeTo(2000, 500).slideUp(500, function () {
                $("#badurl-alert").slideUp(500);
            });
            return;;
        }

        set_button_loading();
        if (url.includes("playlist")) {
            get_playlist(url);
        } else {
            get_video(url);
        }
    });

    $('body').on('click', '.btnplaylistitemdownload', function () {
        var url = $(this).attr("url");
        // console.log("Clicked : " + url);
        set_button_loading($(this).prop("id"));
        get_video(url, $(this).prop("id"));
    });

    $('a#downloadPlaylist').bind('click', function () {
        set_button_loading($(this).prop("id"));

        var data = {};
        data['url_list'] = [];
        data['list_name'] = $("#playlisttitle").text();
        i=0;
        $(".ckbplaylistitem").each(function () {
            if (this.checked) {
                ckbid = $(this).prop("id");
                itemid = ckbid.replace("ckb", "");
                url = $("#downloadbutton" + itemid).attr("url");
                data['url_list'][i] = url;
                i += 1;
            }
        });

        $.ajax({
            type: "POST",
            url: '/api/trigger_download',
            data: JSON.stringify(data),
            contentType: "application/json",
            success: function(response) {
                console.log(response);
                schedule_status_updates(response['download_id']);

                // $currloc = window.location.href.split('?')[0].split('#')[0];
                // $("a#downloadlink").attr("href", $currloc + 'getfile?downloadid=' + response.downloadid);
                // $("a#downloadlink").text($("#playlisttitle").text());
                // $("div#downloadlinkdiv").show();
                // set_button_normal("downloadPlaylist");
                // window.location.href = $currloc + 'getfile?downloadid=' + response.downloadid
            }
        });


        // v2 async

        // $.post("/api/trigger_download", JSON.stringify(data), function(result){
        //     console.log(result);
        //     set_button_normal("downloadPlaylist");
        // });
        
    });

});

function get_video(url, btnid="") {

    console.log("download_clicked()")
    $("div#downloadlinkdiv").hide();

    // start_progress_bar();
    // alert(url);
    $.getJSON($SCRIPT_ROOT + '/_download/single', {
        "url": url
    }, function (data) {
        $currloc = window.location.href.split('?')[0].split('#')[0];
        // alert($currloc + 'getfile?downloadid=' + data.downloadid);
        $("a#downloadlink").attr("href", $currloc + 'getfile?downloadid=' + data.downloadid);
        $("a#downloadlink").text(data.ydl_info['title']);
        $("div#downloadlinkdiv").show();
        $('.progress-bar-label').text("Done");
        set_button_normal(btnid);
        window.location.href = $currloc + 'getfile?downloadid=' + data.downloadid
    });

    $.get($SCRIPT_ROOT + '/cleanup')

    return false;
}

function get_playlist(url) {
    console.log("url: " + url);


    $("#playlisttable tr").slice(1).remove();

    // // alert("url: " + url)
    $.getJSON($SCRIPT_ROOT + '/_getplaylistitems', {
        "url": url
    }, function (ydl_info) {
        // console.log(ydl_info);
        $("#playlisttitle").text(ydl_info['title']);
        $("#playlistdiv").show();

        entries = ydl_info['entries'];

        for (var i = 0; i < entries.length; i++) {
            var item = entries[i];

            row = "<tr>";
            col = "<td><input type=\"checkbox\" class=\"ckbplaylistitem\" id=\"ckb" + item['playlist_index'] + "\" value=\"playlist_index" + item['playlist_index'] + " \"></td>";

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
            row += "<td> \
                        <a href=\"#\" id=\"download" + item['playlist_index'] + "\"> \
                            <button role=\"button\" class=\"btn btn-primary btnplaylistitemdownload\" type=\"button\" id=\"downloadbutton" + item['playlist_index'] + "\" \
                              url=\"" + item['webpage_url'] + "\" > \
                                <span class=\"spinner-border spinner-border-sm\" id=\"loadingspinner" + item['playlist_index'] + "\" role=\"status\" aria-hidden=\"true\" \
                                    style=\"display: none;\"></span> \
                                <span id=\"downloadbuttontext" + item['playlist_index'] + "\"> \
                                    <i class=\"material-icons\">get_app</i> \
                                </span> \
                            </button> \
                        </a> \
                    </td>";
            row += "</tr>";

            $('#playlisttable').append(row);

        }

        set_button_normal();
        $('button#downloadbutton').addClass('btn-secondary').removeClass('btn-primary');
        $(".ckbplaylistitem").prop("checked", true);
        $("input#ckball").prop("checked", true);
        update_playlist_download_count();
        $("button#downloadplaylistbutton").focus();

    });

    $.get($SCRIPT_ROOT + '/cleanup')

}

function isHidden(el) {
    return (el.offsetParent === null)
}

function set_button_loading(btnid="") {
    if(btnid == "downloadplaylistbutton" || btnid == "downloadPlaylist" ) {
        $("span#loadingspinnerplaylist").show();
        $("span#downloadplaylistbuttontext").text("Downloading...");
        $("button#downloadplaylistbutton").prop("disabled", true);
    } else {
        var itemid = 0;
        itemid = btnid.replace("downloadbutton", "");
        if(itemid != 0) {
            $("span#loadingspinner"+itemid).show();
            $("span#downloadbuttontext"+itemid).hide();
            $("button#downloadbutton"+itemid).prop("disabled", true);
        } else {
            $("span#loadingspinner").show();
            $("span#downloadbuttontext").text("Downloading...");
            $("button#downloadbutton").prop("disabled", true);
        }
    }
}

function set_button_normal(btnid="") {
    if(btnid == "downloadplaylistbutton" || btnid == "downloadPlaylist" ) {
        $("span#loadingspinnerplaylist").hide();
        update_playlist_download_count();
        $("button#downloadplaylistbutton").prop("disabled", false);
    } else {
        var itemid = 0;
        itemid = btnid.replace("downloadbutton", "");
        if(itemid != 0) {
            $("span#loadingspinner"+itemid).hide();
            $("span#downloadbuttontext"+itemid).show();
            $("button#downloadbutton"+itemid).prop("disabled", false);
        } else {
            $("span#loadingspinner").hide();
            $("span#downloadbuttontext").text("Download");
            $("button#downloadbutton").prop("disabled", false);
        }
    }
   
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

function update_playlist_download_count() {
    var checkedCount = 0;
    $(".ckbplaylistitem").each(function () {
        if (this.checked) {
            checkedCount += 1;
        }
    });
    // console.log("Download Count : " + checkedCount);
    $("span#downloadplaylistbuttontext").text("Download (" + checkedCount + ")");
}

var status_update_job
function schedule_status_updates(download_id) {
//   $('.progress-bar').css('width', 0 + '%').attr('aria-valuenow', 0);
//   $('.progress-bar-label').text(0 + '%');
//   $("#progressdiv").show();
  status_update_job = setInterval(function(){
    update_download_status(download_id)
  }, 1000);
}

function update_download_status(download_id) {
    // console.log("called update_download_status");
    var data = {};
    data['download_id'] = download_id;
    $.ajax({
        type: "POST",
        url: '/api/get_download_status',
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(response) {
            // console.log(response);
            download_status = response['job_status'];

            if($("div#downloadlinkdiv").is(":hidden")){
                $("div#downloadlinkdiv").show();
            }
            if(download_status != "finished" && download_status !="failed"){
                // console.log("download_status is: " + download_status);
                $("a#downloadlink").text(download_status);
            } else if(download_status == "finished"){
                download_url = response['download_url'];
                $("a#downloadlink").attr("href", download_url);
                $("a#downloadlink").text($("#playlisttitle").text());
                clearInterval(status_update_job);
                set_button_normal("downloadPlaylist");
                window.location.href = download_url;
            } else if(download_status == "failed"){
                $("a#downloadlink").text("Download Failed");
                clearInterval(status_update_job);
                set_button_normal("downloadPlaylist");
            } else {
                $("a#downloadlink").text("Download Failed");
                clearInterval(status_update_job);
                set_button_normal("downloadPlaylist");
            }
            
            // set_button_normal("downloadPlaylist");

            // $currloc = window.location.href.split('?')[0].split('#')[0];
            // $("a#downloadlink").attr("href", $currloc + 'getfile?downloadid=' + response.downloadid);
            // $("a#downloadlink").text($("#playlisttitle").text());
            // $("div#downloadlinkdiv").show();
            // set_button_normal("downloadPlaylist");
            // window.location.href = $currloc + 'getfile?downloadid=' + response.downloadid
        }
    });

}