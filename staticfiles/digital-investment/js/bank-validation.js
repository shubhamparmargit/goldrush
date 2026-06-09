// $(document).ready(function () {
    var path = window.APP_URLS.save_bank_data;

    // Validation Rules
    const validationRules = {
        bank_name: { pattern: /^[A-Za-z.&\s]+$/, message: "Please input alphabet characters only." },
        account_holder_name: { pattern: /^[A-Za-z.\s]+$/, message: "Please input alphabet characters only." },
        account_number: { pattern: /^[0-9]+$/, message: "Please enter a valid account number." }, 
        ifsc_code: { pattern: /^[A-Za-z]{4}0[A-Z0-9a-z]{6}$/, message: "Please enter valid IFSC code" },
        branch_name: { pattern: /^[A-Za-z.\s]+$/, message: "Please input alphabet characters only." }, 
    };
    
    // Allowed File Types
    // const allowedFileExtensions = /(\.pdf|\.doc|\.docx|\.ppt|\.pptx)$/i;
    const allowedFileExtensions = /(\.jpg|\.jpeg|\.png|\.pdf)$/i;
    const maxFileSize = 5 * 1024 * 1024; // 5MB

    const fileErrorMessage = "Invalid file type! Only JPG, PNG and PDF files are allowed.";
    const fileSizeErrorMessage = "File size should not exceed 5MB.";

    // Validate Input Fields
    $(document).on("input", Object.keys(validationRules).map(id => `#${id}`).join(", "), function () {
        validateField(this);
    });

    $(document).on("change", "select.required", function () {
        if ($(this).val() !== "") {
            removeError(this.id);
        }
    });

    // Validate File Inputs
    $(document).on("change", ".filedata", function () {
        validateFile(this);
    });

    // Button Click Validation
    $(".btn_submitBankForm").click(function (e) {
        e.preventDefault();

        let button = $(this); // Get the clicked button
        buttonId = button.attr("id"); // Get button ID

        let isValid = true;

        // Validate Required Fields
        $(".submitBankForm .required").each(function () {
            if ($(this).val().trim() === "") {
                showError($(this).attr("id"), `Please enter ${$(this).attr("placeholder") || "this field"}`);
                isValid = false;
            }
        });

        $(".requiredFile").each(function() {   
            let fileInput = $(this);
            let fileId = fileInput.attr("id");
        
            if (!fileInput[0].files || fileInput[0].files.length === 0) { 
                showError(fileId, `Please select a file for ${fileId}`);
                isValid = false;
            } else {
                removeError(fileId);
            }
        });

        //Extra validation bcoz cancelled cheque and passbook me se ek upload chahiye
        // Validate Cancelled Cheque OR Passbook
        let cancelledCheque = $("#cancelled_cheque")[0].files.length;
        let passbook = $("#passbook")[0].files.length;

        if (!cancelledCheque && !passbook) {
            showError("file_error", "Upload Cancelled Cheque or Passbook");
            isValid = false;
        } else {
            removeError("file_error");
        }
        
        // Validate Pattern Fields
        Object.keys(validationRules).forEach(fieldId => {
            let field = $(`#${fieldId}`);
            if (field.length > 0) isValid = validateField(field[0]) && isValid;
        });
        
        // Validate File Fields
        $(".filedata").each(function () {
            isValid = validateFile(this) && isValid;
        });

        // Submit Form if Valid
        if (isValid) {
            submitForm();
        }
    });

    function formatFileId(fileId) {
        return fileId.replace(/_/g, " ").replace(/\b\w/g, char => char.toUpperCase()); 
    }

    // Function to Validate a Single Field
    function validateField(field) {
        let id = field.id;
        let value = field.value.trim();
        let rule = validationRules[id];

        if (rule && value !== "") {
            if (!rule.pattern.test(value)) {
                showError(id, rule.message);
                return false;
            } else {
                removeError(id);
            }
        }
        return true;
    }

    // Function to Validate File Input
    function validateFile(fileInput) 
    {
        let id = fileInput.id;
        let file = fileInput.files[0];

        if (file) {

            // Check file extension
            if (!allowedFileExtensions.test(file.name)) {
                showError(id, fileErrorMessage);
                fileInput.value = "";
                return false;
            }

            // Check file size
            if (file.size > maxFileSize) {
                showError(id, fileSizeErrorMessage);
                fileInput.value = "";
                return false;
            }

            removeError(id);
            removeError("file_error");
        }

        return true;
    }

    function showError(id, message) {
        let inputField = $(`#${id}`);
        let errorLabel = $(`label[for="${id}-error"]`);
    
        // Agar label already hai, toh message update kar do (dobara render avoid karne ke liye)
        if (errorLabel.length) {
            errorLabel.text(message);
            return;
        }
    
        let errorHtml = `<label for="${id}-error" class="errorValidation" style="color:red; display:block; font-size:12px;">${message}</label>`;
    
        if (inputField.attr("type") === "file") {
            // File input ke error ko thoda delay se render karna (300ms)
            setTimeout(() => {
                if (inputField.parent().is("div")) {
                    inputField.parent().append(errorHtml);
                } else {
                    inputField.after(errorHtml);
                }
            }, 300); 
        } 
        else if (inputField.attr("type") === "checkbox") {
            inputField.closest(".form-group").append(errorHtml);
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
        $(".btn_submitBankForm").prop("disabled", true);    
        $.ajax({
            type: "POST",
            url: path,
            data: new FormData($(".submitBankForm")[0]),
            processData: false,
            contentType: false,
            dataType: "json",
            success: function (response) {
                // console.log(response)
                if(response.success == 1) 
                {
                    showToast("success", response.message);
                    $(".errorValidation").remove(); // Remove all error messages
                    $(".submitBankForm")[0].reset();
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
                $(".btn_submitBankForm").prop("disabled", false);
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