
$(function () {
    $('a#download').bind('click', function() {

            console.log("download_clicked()")
            $("div#downloadlinkdiv").hide();
        
            url = $("input#url").val();
            const regex = RegExp('(http\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+');
        
            if (regex.test(url) == false) {
                console.log("Bad URL: " + url)
                // alert("Bad URL: " + url);
                $("#badurl-alert").fadeTo(2000, 500).slideUp(500, function () {
                    $("#badurl-alert").slideUp(500);
                });
                return;;
            }
        
            set_button_loading();
            // start_progress_bar();
            // alert(url);
            $.getJSON($SCRIPT_ROOT + '/_download', {
                "url": url
            }, function (data) {
                $currloc = window.location.href.split('?')[0].split('#')[0];
                // alert($currloc + 'getfile?downloadid=' + data.downloadid);
                $("a#downloadlink").attr("href", $currloc + 'getfile?downloadid=' + data.downloadid);
                $("div#downloadlinkdiv").show();
                set_button_normal();
                $('.progress-bar-label').text("Done");
                window.location.href = $currloc + 'getfile?downloadid=' + data.downloadid
            });
        
            $.get($SCRIPT_ROOT + '/cleanup')
        
            return false;
    } );


    // $('a#downloadplaylista').bind('click', function() {
    //     alert("fired")
    //     $.get('/_getplaylistitems', {"url": url})
    // });

});

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
