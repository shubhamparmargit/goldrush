// $(document).ready(function () {
    var path = window.APP_URLS.saveTradingUser;
    var buttonId = "";
    // Validation Rules
    const validationRules = {
        franchise_name: { pattern: /^[A-Za-z.\s]+$/, message: "Please input alphabet characters only." },
        holder_name: { pattern: /^[A-Za-z.\s]+$/, message: "Please input alphabet characters only." },
        email: { pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/, message: "Please enter a valid email address." },
        mobile: { pattern: /^[0-9]{10}$/, message: "Please enter a valid 10-digit mobile number." },
        address: { pattern: /^[A-Za-z0-9\s.,@#\-\/]+$/, message: "Invalid characters in address" },
        aadhaar_number: { pattern: /^[0-9]{12}$/, message: "Aadhar card should be 12 digits long." },
        pan_number: { pattern: /^([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}?$/, message: "Please enter a valid PAN card number." },
        gst_number: { pattern: /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/, message: "Please enter a valid GST number" },
        agent_id: { pattern: /^[A-Za-z0-9\-]+$/, message: "Invalid agent id" },
        bank_name: { pattern: /^[A-Za-z.&\s]+$/, message: "Please input alphabet characters only." },
        account_holder_name: { pattern: /^[A-Za-z.\s]+$/, message: "Please input alphabet characters only." },
        account_number: { pattern: /^[0-9]+$/, message: "Please enter a valid account number." }, 
        ifsc_code: { pattern: /^[A-Za-z]{4}0[A-Z0-9a-z]{6}$/, message: "Please enter valid IFSC code" },
        branch_name: { pattern: /^[A-Za-z.\s]+$/, message: "Please input alphabet characters only." }, 
        commission_slab: { pattern: /^[0-9]+$/, message: "Please enter a valid commission slab." }, 
        commission_percentage: { pattern: /^[0-9]+$/, message: "Please enter a valid commission percentage." }, 
    };
    
    // Allowed File Types
    // const allowedFileExtensions = /(\.pdf|\.doc|\.docx|\.ppt|\.pptx)$/i;
    // const fileErrorMessage = "Invalid file type! Only PDF, Word, and PowerPoint files are allowed.";
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
    $(".btn_submitForm").click(function (e) {
        e.preventDefault();

        let button = $(this); // Get the clicked button
        buttonId = button.attr("id"); // Get button ID

        // if(buttonId=="btn_addAgency")
        // {
        //     path = "includes/users.php";
        // }
        // else if(buttonId=="btn_addTeamLeader")
        // {
        //     path = "includes/users.php";
        // }
        // else if(buttonId=="btn_addFOS")
        // {
        //     path = "includes/users.php";
        // }
    
        let isValid = true;

        // Validate Required Fields
        $(".submitForm .required").each(function () {
            if ($(this).val().trim() === "") {
                showError($(this).attr("id"), `Please enter ${$(this).attr("placeholder") || "this field"}`);
                isValid = false;
            }
        });

        // alert("1::"+isValid)

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
        // alert("2::"+isValid)
        // Validate Checkbox
        // if (!$("#coc").is(":checked")) {
        //     showError("coc", "You must agree to the terms.");
        //     isValid = false;
        // } else {
        //     removeError("coc");
        // }

        // if (!$("#cibil_concent").is(":checked")) {
        //     showError("cibil_concent", "You must agree to the terms.");
        //     isValid = false;
        // } else {
        //     removeError("cibil_concent");
        // }
    
        // Validate Pattern Fields
        Object.keys(validationRules).forEach(fieldId => {
            let field = $(`#${fieldId}`);
            if (field.length > 0) isValid = validateField(field[0]) && isValid;
        });
        // alert("3::"+isValid)
        // Validate File Fields
        $(".filedata").each(function () {
            isValid = validateFile(this) && isValid;
        });

        // Submit Form if Valid
        // alert("4::"+isValid)
        if (isValid) {
            submitForm();
        }
    });

    // Checkbox Event: Error remove when checked
    // $("#coc").change(function () {
    //     if ($(this).is(":checked")) {
    //         removeError("coc");
    //     }
    //     else
    //     {
    //         showError("coc", "You must agree to the terms.");
    //         isValid = false;
    //     }
    // });

    // $("#cibil_concent").change(function () {
    //     if ($(this).is(":checked")) {
    //         removeError("cibil_concent");
    //     }
    //     else
    //     {
    //         showError("cibil_concent", "You must agree to the terms.");
    //         isValid = false;
    //     }
    // });

    $('#franchise_model').on('change', function() 
    {
        let model = $(this).val();

        if(model == 'SMRA') {
            $('#parent_div').hide();
            $('#parent_franchise').removeClass('required');
            $('#parent_franchise').html('<option value="">Root Franchise</option>');
        } else {
            $('#parent_div').show();
            $('#parent_franchise').addClass('required');
            fetchParentList(model);
        }
    });

    function fetchParentList(model) 
    {
        $.ajax({
            type: 'POST',
            url: window.APP_URLS.getParentFranchises,
            data: { csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val(),'franchise_model': model },
            success: function(res) {
                let options = '<option value="">Select Parent</option>';
                res.parents.forEach(function(parent){
                    options += `<option value="${parent.unique_id}">${parent.franchise_name} (${parent.referral_id})</option>`;
                });
                $('#parent_franchise').html(options);
            }
        });
    }

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
    function validateFile(fileInput) {
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
    function submitForm() {
        // alert("hello")
        $("#loaderAjax").css("display", "flex");
        $(".btn_submitForm").prop("disabled", true);    
        // alert("hello 1")
        $.ajax({
            type: "POST",
            url: path,
            data: new FormData($(".submitForm")[0]),
            processData: false,
            contentType: false,
            dataType: "json",
            success: function (response) {
                // console.log(response)
                if(response.success == 1) 
                {
                    showToast("success", response.message);
                    $(".errorValidation").remove(); // Remove all error messages
                    
                    $(".submitForm")[0].reset();

                    $('#parent_div').hide();
                    $('#parent_franchise').removeClass('required');
                    $('#parent_franchise').html('<option value="">Root Franchise</option>');

                    // if(buttonId=="btn_addAgency")
                    // {
                    //     window.location.reload();
                    // }
                    // else if(buttonId=="btn_addTeamLeader")
                    // {
                    //     $('#agency').val(null).trigger('change');
                    // }
                    // else if(buttonId=="btn_addFOS")
                    // {
                    //     fill_agency();
                    //     $('#team_leader').val(null).trigger('change');
                    // }
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
                $(".btn_submitForm").prop("disabled", false);
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