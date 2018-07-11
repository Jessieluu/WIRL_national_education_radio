var channel = {}
$.ajax({ //load進channel名單
    url: 'https://www.ner.gov.tw/api/programs',
    type: "GET",
    success: function (msg) {
        document.getElementById("showChannel").innerHTML = "";
        channel = msg;
        $("[id$=showChannel]").append($("<option></option>").attr("selected", "").attr('disabled', 'disabled').text("帶入節目名稱"));
        for (var i = 0; i < channel.rows.length; i++) { //將取得的Json一筆一筆放入清單
            $("[id$=showChannel]").append($("<option></option>").attr("value", channel.rows[i].name).text(msg.rows[i].name));
        }
    },
    error: function (xhr, ajaxOptions, thrownError) {
        alert(xhr.status);
    }
});

function showInfo(){
    var channel_title = $("#showChannel").val();
    let channel_id = "";
    let channel_catelog = "";
    let channel_memo = "";
    for(let i in channel.rows){
        if(channel_title === channel.rows[i].name){
            channel_id = channel.rows[i]._id;
            channel_memo = channel.rows[i].introduction;
        }
    }
    channel_memo = channel_memo.replace(/<(.|\n)*?>/g, '');

    document.getElementById("showChannelMemo").innerHTML = channel_memo;
}

$( "#copy1" ).click(function() {
     document.getElementById('channel_name').value = document.getElementById('showChannel').value;
     return false;
});

$( "#copy2" ).click(function() {
    document.getElementById('channel_category').value = document.getElementById('showChannelCatelog').value;
    return false;
});

$( "#copy3" ).click(function() {
    document.getElementById('channel_memo').value = document.getElementById('showChannelMemo').value;
    return false;
});
