$( document ).ready(function() {

    // On reload open the download tab
    setTimeout(() => {

        var hash = window.location.hash;
        if (hash != ''){
            hash = hash. substring(1);
            var nav = '#nav-';
            var tab = '-tab';
            hash = nav.concat(hash);
            hash = hash.concat(tab);
            var hash1 = hash.substring(0,hash.length - 4);

            $(".tab-pane").removeClass('show');
            $(".tab-pane").removeClass('active');

            $(".nav-link").removeClass('active');
            $(".nav-link").attr('aria-selected', false);

            $(hash).addClass('active');
            $(hash).attr('aria-selected', true);
            $(hash).removeAttr('tabindex');

            $(hash1).addClass('active');
            $(hash1).addClass('show');

            $(hash).trigger( "click" );
        }

    }, "500");

    // On click open the download tab
    $(".click-trigger").click(function(){

        setTimeout(() => {

            var hash = window.location.hash;
            hash = hash. substring(1);
            var nav = '#nav-';
            var tab = '-tab';
            hash = nav.concat(hash);
            hash = hash.concat(tab);
            var hash1 = hash.substring(0,hash.length - 4);

            $(".tab-pane").removeClass('show');
            $(".tab-pane").removeClass('active');

            $(".nav-link").removeClass('active');
            $(".nav-link").attr('aria-selected', false);

            $(hash).addClass('active');
            $(hash).attr('aria-selected', true);
            $(hash).removeAttr('tabindex');

            $(hash1).addClass('active');
            $(hash1).addClass('show');

            $(hash).trigger( "click" );

        }, "200");

    });

    // On click show loader
    $("form").submit(function(){
        $('.loader').show();
    });

    // Validate input URL for private downloader

    setInterval(function (){

        var url = $('#url').val();

        if (url != ''){
            let domain = (new URL(url));
            domain = domain.hostname;
            if (domain == 'www.instagram.com'){
                const regex_p = new RegExp("/p/",);
                const regex_v = new RegExp("/reel/",);
                if ((regex_p.test(url)) || regex_v.test(url)){
                    url = url.replace(/\?.*$/g,"");
                    url = url+'?__a=1&__d=dis';
                    $('#scrap_url').val(url);
                }else{
                    $('#url').val('');
                    $('#scrap_url').val('');
                    alert("The URL you pasted is not an Instagram post URL!");
                }
            }else{
                $('#url').val('');
                $('#scrap_url').val('');
                alert("The URL you pasted is not an Instagram URL!");
            }
        }else{
            $('#scrap_url').val('');
        }

    },1000)


});


