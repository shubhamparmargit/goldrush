let validator = new FormValidator("#contactForm", {

    name: {
        required: "Name is required",
        regex: /^[A-Za-z\s]{2,50}$/,
        invalid: "Only letters allowed"
    },

    email: {
        required: "Email is required",
        regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        invalid: "Invalid email"
    },

    phone: {
        required: "Phone number is required",
        regex: /^[0-9]{10}$/,
        invalid: "Enter valid 10 digit phone"
    },

    message: {
        required: "Message is required",
        min: 10,
        minMsg: "Message must be at least 10 characters"
    }

})

$("#contactForm").on("validSubmit", function () {

    let btn = $("#contactForm button[type=submit]")
    let originalText = btn.text()

    btn.prop("disabled", true).text("Sending...")

    let formData = new FormData(this)

    $.ajax({

        url: window.APP_URLS.contactsubmit,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val()
        },

        success: function (res) {

            btn.prop("disabled", false).text(originalText)

            if (res.success) {

                $("#contactForm")[0].reset()

                $("#formMessage").html(
                    '<div class="form-success">' + res.message + '</div>'
                )

            } else {

                $("#formMessage").html(
                    '<div class="form-fail">' + res.message + '</div>'
                )

            }

        },

        error: function () {

            btn.prop("disabled", false).text(originalText)

            $("#formMessage").html(
                '<div class="form-fail">Server error</div>'
            )

        }

    })

})