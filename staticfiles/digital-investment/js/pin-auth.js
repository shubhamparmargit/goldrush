$(document).ready(function () {
    document.querySelector(".pin-input").focus();
})
// Apply for both rows
handlePinInputs(".pin-input");
handlePinInputs(".confirm-pin");

let mode = document.getElementById("pinMode").value;

document.getElementById("pinForm").addEventListener("submit", function (e) {
    e.preventDefault();

    let pin = "";
    let confirmPin = "";

    document.querySelectorAll(".pin-input").forEach(input => {
        pin += input.value;
    });

    if (pin.length !== 6) {
        $.toast({ text: "Please enter complete 6-digit PIN", icon: "error" });
        return;
    }

    if (mode === "setup") {
        document.querySelectorAll(".confirm-pin").forEach(input => {
            confirmPin += input.value;
        });

        if (confirmPin.length !== 6) {
            $.toast({ text: "Please confirm your 6-digit PIN", icon: "error" });
            return;
        }

        if (pin !== confirmPin) {
            $.toast({ text: "PIN does not match", icon: "error" });
            return;
        }
    }

    let url = window.APP_URLS.handle_pin;

    let btn = document.querySelector(".primary-btn");
    btn.disabled = true;
    btn.innerText = "Processing...";

    $.ajax({
        url: url,
        type: "POST",
        data: {
            mode: mode,
            pin: pin,
            confirm_pin: confirmPin,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function (res) {

            btn.disabled = false;
            btn.innerText = mode === "setup"
                ? "Set PIN & Continue"
                : "Verify & Continue";

            if (res.success) {
                window.location.href = res.redirect;
            }
            else {

                if (res.locked_until) {
                    $.toast({ text: "Account locked. Try again later.", icon: "error" });
                    location.reload();
                    return;
                }

                if (res.attempts_remaining !== undefined) {

                    let attemptBox = document.querySelector(".pin-attempt-info");

                    // If not exist → create it
                    if (!attemptBox) {

                        attemptBox = document.createElement("div");
                        attemptBox.className = "pin-attempt-info text-danger mt-3 text-center";

                        document.querySelector("#pinForm").appendChild(attemptBox);
                    }

                    attemptBox.innerText = res.attempts_remaining + " attempts remaining";
                }

                $.toast({ text: res.message || "Invalid PIN", icon: "error" });

                // Clear inputs
                document.querySelectorAll("input[type='password']").forEach(i => i.value = "");
                document.querySelector(".pin-input").focus();
            }
        },
        error: function () {
            btn.disabled = false;
            btn.innerText = "Try Again";
            $.toast({ text: "Something went wrong", icon: "error"});
        }
    });
});