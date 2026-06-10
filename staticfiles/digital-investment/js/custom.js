function closeTrading(){
    if (window.history.length > 1) {
        history.back();
    } else {
        window.close();
    }
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showLoader() {
    document.getElementById("globalLoader").style.display = "flex";
}

function hideLoader() {
    document.getElementById("globalLoader").style.display = "none";
}

function fetchLiveRate() 
{
    const path = window.APP_URLS.getMetalLiveRate;
    // console.log('live-rate')
    fetch(path)
        .then(res => res.json())
        .then(data => { 
            // console.log(JSON.stringify(data, null, 2));
            // console.log('current_gold_rate :: '+data.current_gold_rate)
            // console.log('current_silver_rate :: '+data.current_silver_rate)
            $(".gold-rate").html(data.current_gold_rate);
            $(".silver-rate").html(data.current_silver_rate);
            if (data.currency_icon) {
                $(".currency-icon").html(data.currency_icon);
            }
            document.getElementById("dateTime").innerHTML = data.date_time
        }
    );
}