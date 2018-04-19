var op_code = {
    "PLAY_PAUSE" : 0x01,
    "GO_NEXT_AUDIO" : 0x02,
    "SEEK_BAR" : 0x04,
    "ACTIVE_MODE" : 0x08
};

let playlog_id = {}

$(document).ready(function(){
    $(".play").click(function(){
        $(".play-button").toggle();
        $(".pause-button").toggle();
        $(".background-grey").toggle();
    });
    $(".check a").click(function(){
        recordID = "#record" + $(this).attr("data-record-id");
        console.log(recordID);
        $(recordID).addClass("slideInUp");
        $(recordID).show();
        $(".record-page").addClass("overflow")
    });
    $(".tab a").click(function(){
        $(this).parents(".record").hide();
    });
    $(".skip").click(function(){
        $(".home-page").removeClass("question-toggle");
        $(".question-block").hide();
    });
    $("#right_menu").on('click', function(){
        var audio_id = $("#right_menu li").val();
        get_play_log(audio_id, op_code.GO_NEXT_AUDIO, str(audio_id));
    });
    $("#switch").on('change', function(){
        var audio_id_switch = $("#switch").val();
        var bool = $("#switch").is(':checked');
        if(bool == 1)
            bool = "true";
        else
            bool = "false";
        get_play_log(audio_id_switch, op_code.ACTIVE_MODE, bool);
    });
});

function buttonUp(){
         var valux = $('.sb-search-input').val(); 
            valux = $.trim(valux).length;
            if(valux !== 0){
                $('.sb-search-submit').css('z-index','99');
            } else{
                $('.sb-search-input').val(''); 
                $('.sb-search-submit').css('z-index','-999');
            }
    }
    
    $(document).ready(function(){
        var submitIcon = $('.sb-icon-search');
        var submitInput = $('.sb-search-input');
        var searchBox = $('.sb-search');
        var isOpen = false;
        
        $(document).mouseup(function(){
            if(isOpen == true){
            submitInput.val('');
            $('.sb-search-submit').css('z-index','-999');
            submitIcon.click();
            }
        });
        
        submitIcon.mouseup(function(){
            return false;
        });
        
        searchBox.mouseup(function(){
            return false;
        });
                
        submitIcon.click(function(){
            if(isOpen == false){
                searchBox.addClass('sb-search-open');
                isOpen = true;
            } else {
                searchBox.removeClass('sb-search-open');
                isOpen = false;
            }
    });

});

$(document).ready(function(){
    $('.slider-nav').click({
      slidesToShow: 1,
      slidesToScroll: 1,
      arrows: false,
      fade: true,
      adaptiveHeight: true,
    });
    $('.series').click({
      slidesToShow: 3,
      slidesToScroll: 1,
      asNavFor: '.slider-for',
      dots: true,
      focusOnSelect: true,
      arrows: true,
      asNavFor: '.slider-nav',
      responsive: [
        {
          breakpoint: 992,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1,
          }
        }
      ]
    });
});

function get_play_log(audio_id, operation_code, operation_value) {
    $.ajax({
        type: 'POST',
        url: '/radio/get_playlog',
        data: JSON.stringify({
            'audio_id' : audio_id
        }),
        contentType: "application/json; charset=utf-8",
    }).done(function(msg) {
        var json = msg;
        playlog_id = JSON.parse(json);
        add_op_log(playlog_id['playlog_id'], operation_code, operation_value);
        
    });
}

function add_op_log(play_log, operation_code, operation_value){
    $.ajax({
        type: 'POST',
        url: '/radio/add_oplog',
        data: JSON.stringify({
            'play_log' : play_log,
            'operation_code' : operation_code,
            'operation_value' : operation_value
        }),
        contentType: "application/json; charset=utf-8",
    });
}

var is_show_recommend = false;
function show_recommand(){
    is_show_recommend = !is_show_recommend;

    if(is_show_recommend){
        document.getElementById('recommend_box').style.display='block';
        document.getElementById('channel_list').style.display='none';
    }
    else{
        document.getElementById('recommend_box').style.display='none';
        document.getElementById('channel_list').style.display='block';
    }
       
}

