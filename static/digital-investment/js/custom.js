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

let lastGoldRate = null;
let lastSilverRate = null;

function fetchLiveRate() 
{
    const path = window.APP_URLS.getMetalLiveRate;
    fetch(path)
        .then(res => res.json())
        .then(data => { 
            const newGoldRate = parseFloat(data.current_gold_rate);
            const newSilverRate = parseFloat(data.current_silver_rate);

            // Compare and adjust classes for gold-rate
            $(".gold-rate").each(function() {
                const $el = $(this);
                const $container = $el.closest(".metal-rate");
                if ($container.length) {
                    const prevVal = lastGoldRate || parseFloat($el.text());
                    $container.find(".rate-arrow").remove();
                    if (prevVal && newGoldRate > prevVal) {
                        $container.addClass("rate-up").removeClass("rate-down");
                        $container.prepend('<span class="rate-arrow" style="margin-right: 4px; font-size: 14px;">▲</span>');
                    } else if (prevVal && newGoldRate < prevVal) {
                        $container.addClass("rate-down").removeClass("rate-up");
                        $container.prepend('<span class="rate-arrow" style="margin-right: 4px; font-size: 14px;">▼</span>');
                    }
                }
            });

            // Compare and adjust classes for silver-rate
            $(".silver-rate").each(function() {
                const $el = $(this);
                const $container = $el.closest(".metal-rate");
                if ($container.length) {
                    const prevVal = lastSilverRate || parseFloat($el.text());
                    $container.find(".rate-arrow").remove();
                    if (prevVal && newSilverRate > prevVal) {
                        $container.addClass("rate-up").removeClass("rate-down");
                        $container.prepend('<span class="rate-arrow" style="margin-right: 4px; font-size: 14px;">▲</span>');
                    } else if (prevVal && newSilverRate < prevVal) {
                        $container.addClass("rate-down").removeClass("rate-up");
                        $container.prepend('<span class="rate-arrow" style="margin-right: 4px; font-size: 14px;">▼</span>');
                    }
                }
            });

            // Store for next check
            lastGoldRate = newGoldRate;
            lastSilverRate = newSilverRate;

            // Update values in UI
            $(".gold-rate").html(data.current_gold_rate);
            $(".silver-rate").html(data.current_silver_rate);
            if (data.currency_icon) {
                $(".currency-icon").html(data.currency_icon);
            }
            const dateTimeEl = document.getElementById("dateTime");
            if (dateTimeEl) {
                dateTimeEl.innerHTML = data.date_time;
            }
        }
    );
}