// $(document).ready(function () {
    var path = window.APP_URLS.save_term_data;

    // Button Click Validation
    $(".btn_submitTermsForm").click(function (e) {
        e.preventDefault();
        let isValid = true;

        // Validate Checkbox
        if (!$("#accept_terms").is(":checked")) {
            showError("accept_terms", "You must agree to the terms.");
            isValid = false;
        } else {
            removeError("accept_terms");
        }

        // Submit Form if Valid
        if (isValid) {
            submitForm();
        }
    });

    // Checkbox Event: Error remove when checked
    $("#accept_terms").change(function () {
        if ($(this).is(":checked")) {
            removeError("accept_terms");
        }
        else
        {
            showError("accept_terms", "You must agree to the terms.");
            isValid = false;
        }
    });

    function showError(id, message) {
        let inputField = $(`#${id}`);
        let errorLabel = $(`label[for="${id}-error"]`);
    
        // Agar label already hai, toh message update kar do (dobara render avoid karne ke liye)
        if (errorLabel.length) {
            errorLabel.text(message);
            return;
        }
    
        let errorHtml = `<label for="${id}-error" class="errorValidation mb-24" style="color:red; display:block; font-size:12px;">${message}</label>`;
        if (inputField.attr("type") === "checkbox") {
            inputField.closest(".form-group").after(errorHtml);
        } 
        else {
            inputField.after(errorHtml); // Normal fields ke liye turant show
        }
    }
    
    function removeError(id) {
        setTimeout(() => {
            $(`label[for="${id}-error"]`).remove(); // Remove the error label
        }, 50);
    }
    
    // Submit Form via AJAX
    function submitForm() 
    {
        $("#loaderAjax").css("display", "flex");
        $(".btn_submitTermsForm").prop("disabled", true);    

        $.ajax({
            type: "POST",
            url: path,
            data: new FormData($(".submitTermsForm")[0]),
            processData: false,
            contentType: false,
            dataType: "json",
            success: function (response) {
                // console.log(response)
                if(response.success == 1) 
                {
                    showToast("success", response.message);
                    $(".errorValidation").remove(); // Remove all error messages
                    
                    $(".submitTermsForm")[0].reset();
                    window.location.assign(response.redirectURL);
                } 
                else if(response.success == 0)
                {
                    showToast("error", response.message);
                }
                else 
                {
                    showToast("error", response.message);
    
                    if (response.errors) {
                        Object.keys(response.errors).forEach(fieldId => {
                            showError(fieldId, response.errors[fieldId]);
                        });
                    }
                }
            },
            error: function(jqXHR, textStatus, error) 
            {
                $("#loaderAjax").css("display", "none");
                // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
                showToast("error", "Something went wrong. Please try again later.");
            },
            complete: function () {
                // Hide loader and enable submit button
                $("#loaderAjax").css("display", "none");
                $(".btn_submitTermsForm").prop("disabled", false);
            }
        });
    }    

    // Show Toast Message
    function showToast(type, message) {
        $.toast({
            heading: type === "success" ? "Success" : "Error",
            text: message,
            position: "top-right",
            loaderBg: "#ff6849",
            icon: type,
            hideAfter: 3500,
        });
    }
// });