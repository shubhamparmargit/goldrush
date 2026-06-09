$(document).ready(function()
{
    (function($) 
    {
        "use strict";
        $("#reveal").on('change',function(e) 
        {
            var $password = $("#password");
            if(this.checked==true)
            {
                $password.attr('type', 'text');
            }
            else
            {
                $password.attr('type', 'password');
            }
        });

        $("#btn_login").click(function(e) 
        {
            $('#frm_login').validate(
            {
                rules:
                {
                    username: 
                    {
                        required: true,
                        minlength:10,
                        maxlength:10,
                        digits:true
                    },
                    password: 
                    {
                        required: true
                    }
                },
                messages:
                {
                    username: 
                    {
                        required: "Username can't be blank!",
                        minlength:"Only 10 characters allowed",
                        maxlength:"Only 10 characters allowed",
                        digits:"Only numbers allowed"
                    },
                    password: 
                    {
                        required: "Password can't be blank!"
                    }
                },
                submitHandler: function(form) 
                {
                    $("#btn_login").attr({"data-indicator":"on","disabled":"disabled"});
                    $("#frm_login :input").prop('readonly', true);
                    $(form).ajaxSubmit({
                        type:"POST",
                        data:
                        {
                            btn_login:'btn_login',
                            username:$("#username").val(),
                            password:$("#password").val()
                        },
                        url:path,
                        dataType : "json",
                        success: function(response) 
                        {
                            // console.log(response)
                            $("#btn_login").removeAttr("data-indicator disabled");
                            $("#frm_login :input").removeAttr('readonly');
                            try
                            {
                                if(response.success=="1")
                                {
                                    $.toast({
                                        heading: 'Success',
                                        text: response.message,
                                        position: 'top-right',
                                        loaderBg: '#ff6849',
                                        icon: 'success',
                                        hideAfter: 3500,
                                        stack: 6
                                    });
                                    window.location.replace(response.redirect);
                                    var validator = $("#frm_login").validate();
                                    validator.resetForm();
                                }
                                else
                                {
                                    $.toast({
                                        heading: 'Error',
                                        text: response.message,
                                        position: 'top-right',
                                        loaderBg: '#ff6849',
                                        icon: 'error',
                                        hideAfter: 3500
                                    });
                                }
                            }
                            catch(error) 
                            {
                                $.toast({
                                    heading: 'Error',
                                    text: "Sorry, looks like there are some errors detected, please try again.",
                                    position: 'top-right',
                                    loaderBg: '#ff6849',
                                    icon: 'error',
                                    hideAfter: 3500
                                });
                            }
                        },
                        error: function(jqXHR, textStatus, error) 
                        {
                            // console.log(jqXHR+" | "+textStatus+" | "+error)
                            $("#btn_login").removeAttr("data-indicator disabled");
                            $("#frm_login :input").removeAttr('readonly');
                            $.toast({
                                heading: 'Error',
                                text: 'Something went wrong. Please try again later.',
                                position: 'top-right',
                                loaderBg: '#ff6849',
                                icon: 'error',
                                hideAfter: 3500
                            });
                        }
                    })
                    return false;
                }
            })
        })

        $("#btn_password_reset").click(function(e) 
        {
            $('#frm_password_reset').validate(
            {
                errorPlacement: function(error, element) 
                {      
                    $(element).parent('div').after(error);
                },
                rules:
                {
                    email: 
                    {
                        required: true,
                        email:true,
                    }
                },
                messages:
                {
                    email: 
                    {
                        required: "Email can't be blank!",
                        email:"Please enter valid email-id"
                    }
                },
                submitHandler: function(form) 
                {
                    $("#btn_password_reset").attr({"data-indicator":"on","disabled":"disabled"});
                    $("#frm_password_reset :input").prop('readonly', true);
                    $(form).ajaxSubmit({
                        type:"POST",
                        data:
                        {
                            btn_password_reset:'btn_password_reset',
                            email:$("#email").val()
                        },
                        url:password_reset_request,
                        dataType : "json",
                        success: function(response) 
                        {
                            // console.log(response)
                            $("#btn_password_reset").removeAttr("data-indicator disabled");
                            $("#frm_password_reset :input").removeAttr('readonly');
                            try
                            {
                                if(response.success=="1")
                                {
                                    $.toast({
                                        heading: 'Success',
                                        text: response.message,
                                        position: 'top-right',
                                        loaderBg: '#ff6849',
                                        icon: 'success',
                                        hideAfter: 3500,
                                        stack: 6
                                    });
                                    var validator = $("#frm_password_reset").validate();
                                    validator.resetForm();

                                    $(".data").html('<div class="content-top-agile p-20 pb-0">\
                                    <h2 class="text-purple mb-20">Password reset sent</h2>\
                                    <p class="mb-20">We\'ve emailed you instructions for setting password, if an account exists with the email you entered. You should receive them shortly.</p>\
                                    <p class="mb-20">If you don\'t receive an email, please make sure you\'ve entered the address you registered with, and check your spam folder.</p>\
                                    </div>');
                                }
                                else
                                {
                                    $.toast({
                                        heading: 'Error',
                                        text: response.message,
                                        position: 'top-right',
                                        loaderBg: '#ff6849',
                                        icon: 'error',
                                        hideAfter: 3500
                                    });
                                }
                            }
                            catch(error) 
                            {
                                $.toast({
                                    heading: 'Error',
                                    text: "Sorry, looks like there are some errors detected, please try again.",
                                    position: 'top-right',
                                    loaderBg: '#ff6849',
                                    icon: 'error',
                                    hideAfter: 3500
                                });
                            }
                        },
                        error: function(jqXHR, textStatus, error) 
                        {
                            // console.log(jqXHR+" | "+textStatus+" | "+error)
                            $("#btn_password_reset").removeAttr("data-indicator disabled");
                            $("#frm_password_reset :input").removeAttr('readonly');
                            $.toast({
                                heading: 'Error',
                                text: 'Something went wrong. Please try again later.',
                                position: 'top-right',
                                loaderBg: '#ff6849',
                                icon: 'error',
                                hideAfter: 3500
                            });
                        }
                    })
                }
            })
        })

        $("#btn_set_password").click(function(e) 
        {
            $('#frm_set_password').validate(
            {
                errorPlacement: function(error, element) 
                {      
                    $(element).parent('div').after(error);
                },
                rules:
                {
                    password: {
                        required: true
                    },
                    confirm_password: {
                        required: true,
                        equalTo : "#password"
                    }
                },
                messages:
                {
                    password: {
                        required: "Please enter your new password"
                    },
                    confirm_password: {
                        required: "Please confirm your password",
                        equalTo: "Password does not match"
                    }
                },
                submitHandler: function(form) 
                {
                    $("#btn_set_password").attr({"data-indicator":"on","disabled":"disabled"});
                    $("#frm_set_password :input").prop('readonly', true);
                    $(form).ajaxSubmit({
                        type:"POST",
                        data:
                        {
                            btn_set_password:'btn_set_password',
                            password:$("#password").val(),
                            confirm_password:$("#confirm_password").val(),
                        },
                        url:set_new_password,
                        dataType : "json",
                        success: function(response) 
                        {
                            // console.log(response)
                            $("#btn_set_password").removeAttr("data-indicator disabled");
                            $("#frm_set_password :input").removeAttr('readonly');
                            try
                            {
                                var output = ''
                                if(response.success==1)
                                {
                                    $.toast({
                                        heading: 'Success',
                                        text: response.message,
                                        position: 'top-right',
                                        loaderBg: '#ff6849',
                                        icon: 'success',
                                        hideAfter: 3500,
                                        stack: 6
                                    });
                                    var validator = $("#frm_set_password").validate();
                                    validator.resetForm();

                                    if(response.btn)
                                    {
                                        output ='<div class="content-top-agile pt-100 p-20 pb-0">\
                                        <h2 class="text-purple mb-20">Password reset complete</h2>\
                                        <p class="mb-20">Your password has been set. You may go ahead and log in now.</p>\
                                        </div>\
                                        <div class="p-40">\
                                            <div class="row">\
                                                <div class="col-6">\
                                                </div>\
                                                <div class="col-6">\
                                                    <div class="fog-pwd pull-right">\
                                                        <a href="'+login+'" class="hover-warning"><i class="fa fa-lock"></i> Sign In</a><br>\
                                                    </div>\
                                                </div>\
                                            </div>\
                                        </div>';
                                    }
                                    else
                                    {
                                        output ='<div class="content-top-agile pt-50 p-20 pb-50">\
                                        <h2 class="text-purple mb-20">Password reset complete</h2>\
                                        <p class="mb-20">Your password has been set. You may go ahead and log in now.</p>\
                                        </div>';
                                    }
                                }
                                else
                                {
                                    if(response.btn)
                                    {
                                        output = '<div class="content-top-agile pt-100 p-20 pb-0">\
                                            <h2 style="color: red;">Error</h2>\
                                            <p class="mb-20">'+response.message+'</p>\
                                        </div>\
                                        <div class="p-40">\
                                            <div class="row">\
                                                <div class="col-6">\
                                                </div>\
                                                <div class="col-6">\
                                                    <div class="fog-pwd pull-right">\
                                                        <a href="'+login+'" class="hover-warning"><i class="fa fa-lock"></i> Sign In</a><br>\
                                                    </div>\
                                                </div>\
                                            </div>\
                                        </div>';
                                    }
                                    else
                                    {
                                        output = '<div class="content-top-agile pt-50 p-20 pb-50">\
                                            <h2 style="color: red;">Error</h2>\
                                            <p class="mb-20">'+response.message+'</p>\
                                        </div>'
                                    }
                                }

                                $(".data").html(output)
                            }
                            catch(error) 
                            {
                                $.toast({
                                    heading: 'Error',
                                    text: "Sorry, looks like there are some errors detected, please try again.",
                                    position: 'top-right',
                                    loaderBg: '#ff6849',
                                    icon: 'error',
                                    hideAfter: 3500
                                });
                            }
                        },
                        error: function(jqXHR, textStatus, error) 
                        {
                            // console.log(jqXHR+" | "+textStatus+" | "+error)
                            $("#btn_set_password").removeAttr("data-indicator disabled");
                            $("#frm_set_password :input").removeAttr('readonly');
                            $.toast({
                                heading: 'Error',
                                text: 'Something went wrong. Please try again later.',
                                position: 'top-right',
                                loaderBg: '#ff6849',
                                icon: 'error',
                                hideAfter: 3500
                            });
                        }
                    })
                }
            })
        })

        $("#btn_changePassword").click(function(e) 
        {
            $('#frm_changePassword').validate(
            {
                errorPlacement: function(error, element) 
                {      
                    $(element).parent('div').after(error);
                },
                rules:
                {
                    password: {
                        required: true
                    },
                    confirm_password: {
                        required: true,
                        equalTo : "#password"
                    }
                },
                messages:
                {
                    password: {
                        required: "Please enter your new password"
                    },
                    confirm_password: {
                        required: "Please confirm your password",
                        equalTo: "Password does not match"
                    }
                },
                submitHandler: function(form) 
                {
                    $("#btn_changePassword").attr({"data-indicator":"on","disabled":"disabled"});
                    $("#frm_changePassword :input").prop('readonly', true);
                    $(form).ajaxSubmit({
                        type:"POST",
                        data:
                        {
                            password:$("#password").val(),
                            confirm_password:$("#confirm_password").val(),
                            
                        },
                        url:window.APP_URLS.change_login_password,
                        dataType : "json",
                        success: function(response) 
                        {
                            // console.log(response)
                            $("#btn_changePassword").removeAttr("data-indicator disabled");
                            $("#frm_changePassword :input").removeAttr('readonly');
                            try
                            {
                                if(response.success==1)
                                {
                                    $.toast({
                                        heading: 'Success',
                                        text: response.message,
                                        position: 'top-right',
                                        loaderBg: '#ff6849',
                                        icon: 'success',
                                        hideAfter: 3500,
                                        stack: 6
                                    });
                                    var validator = $("#frm_changePassword").validate();
                                    validator.resetForm();
                                }
                                else
                                {
                                    $.toast({
                                        heading: 'Error',
                                        text: response.message,
                                        position: 'top-right',
                                        loaderBg: '#ff6849',
                                        icon: 'error',
                                        hideAfter: 3500
                                    });
                                }
                            }
                            catch(error) 
                            {
                                $.toast({
                                    heading: 'Error',
                                    text: "Sorry, looks like there are some errors detected, please try again.",
                                    position: 'top-right',
                                    loaderBg: '#ff6849',
                                    icon: 'error',
                                    hideAfter: 3500
                                });
                            }
                        },
                        error: function(jqXHR, textStatus, error) 
                        {
                            // console.log(jqXHR+" | "+textStatus+" | "+error)
                            $("#btn_changePassword").removeAttr("data-indicator disabled");
                            $("#frm_changePassword :input").removeAttr('readonly');
                            $.toast({
                                heading: 'Error',
                                text: 'Something went wrong. Please try again later.',
                                position: 'top-right',
                                loaderBg: '#ff6849',
                                icon: 'error',
                                hideAfter: 3500
                            });
                        }
                    })
                }
            })
        })
    })(jQuery);
});