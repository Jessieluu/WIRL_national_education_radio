$.ajax({ 
    url: 'https://www.ner.gov.tw/api/programs?size=99999999&page=1&order=createdAt&desc=true&onShelf=true&overview=true',
    type: "GET",
    success: function (msg) {
        var channel_title = $("#channelName").val();
        console.log(channel_title);
        for (var i = 0; i < msg.rows.length; i++) { 
            if(channel_title === msg.rows[i].name)
                showInfo(msg.rows[i]._id);
        }
    },
    error: function (xhr, ajaxOptions, thrownError) {
        alert(xhr.status);
    }
});

function showInfo(radio){
    $.ajax({ 
    url: 'https://www.ner.gov.tw/api/programlists?size=99999&page=1&order=date&desc=true&withAudio=true&onShelf=true&withProgram=true&program=' + radio,
    type: "GET",
    success: function (msg) {
        document.getElementById("showAudit").innerHTML = "";
        $("[id$=showAudit]").append($("<option></option>").attr("selected", "").attr('disabled', 'disabled').text("帶入音檔名稱"));
        for (var i = 0; i < msg.rows.length; i++) //將取得的Json一筆一筆放入清單
            $("[id$=showAudit]").append($("<option></optiona>").attr("value", msg.rows[i].title).text(msg.rows[i].title));
    },
    error: function (xhr, ajaxOptions, thrownError) {
        alert(xhr.status);
    }
});
}

$( "#copy4" ).click(function() {
    document.getElementById('audio_name').value = document.getElementById('showAudit').value;
    return false;
});
