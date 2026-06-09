$(document).ready(function()
{ 
    var type = $("#type").val();
    var page = 1;
    var query = $('#search').val();
    var from_date = $("#from_date").val();
    var to_date = $("#to_date").val();
    var access = $("#access").val();
    var limit = $("#limit").val();
    var franchise_model = "SMRA";
    var days = $("#days").val();

    if(type=="trading_user")
    {
        $('.franchise-tabs a[title="SMRA"]').addClass('active');
    }

    load_data(page,type);

    $(document).on('click', '.page-link', function()
    {
        page = $(this).data('page_number');
        load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
    });

    $('#search').keyup(function()
    {
        query = $('#search').val();
        $('#search_im').val(query);
        load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
    });

    $('#search').on('search', function () 
    {
        query = '';
        $('#search_im').val('');
        load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
    });

    $("#access").change(function(){
        access=$(this).val();
        $('#access_im').val(access);
        if(access!="")
        {
            load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
        }
    });

    $("#days").change(function(){
        days=$(this).val();
        if(days!="")
        {
            load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
        }
    });

    $("#limit").change(function(){
        limit=$(this).val();
        if(limit!="")
        {
            load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
        }
    });

    $(".franchise-tabs a").on("click",function()
    {
        $(".franchise-tabs a").removeClass("active");
        $(this).addClass("active");  
        $($(this).attr("href")).addClass("active");
        franchise_model=$(this).attr("title");
        // alert(franchise_model)
        page = 1;
        if(franchise_model!="")
        {
            load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
        }
    });

    var start = moment().subtract(29, 'days');
    var end = moment();
    function cb(start, end) {
        $('#reportrange span').html(start.format('MMM D, YYYY') + ' - ' + end.format('MMM D, YYYY'));
        $("#from_date").val(start.format('YYYY-MM-DD'));
        $("#to_date").val(end.format('YYYY-MM-DD'));
        
        $('#from_date_im').val(start.format('YYYY-MM-DD'));
        $('#to_date_im').val(end.format('YYYY-MM-DD'));

        from_date=$("#from_date").val();
        to_date=$("#to_date").val();
        
        load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
    }
    $('#reportrange').daterangepicker({
        locale: {
            format: 'DD-MMM-YYYY'
        },
        startDate: start,
        endDate: end,
        ranges: {
        'Today': [moment(), moment()],
        'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
        'Last 7 Days': [moment().subtract(6, 'days'), moment()],
        'Last 30 Days': [moment().subtract(29, 'days'), moment()],
        'This Month': [moment().startOf('month'), moment().endOf('month')],
        'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    },cb);

    $('#reportrange').on('cancel.daterangepicker', function(ev, picker) {
        $('#reportrange span').html('Filter By Date');
        $('#reportrange').val('');
        $("#from_date").val('');
        $("#to_date").val('');

        $('#from_date_im').val('');
        $('#to_date_im').val('');

        from_date=$("#from_date").val();
        to_date=$("#to_date").val();
        
        load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
    });

    $(document).on('click', '#clear-filter', function(e)
	{
        page=1;
        $('#search').val("");
        $("#limit").val("10").change();
        $("#access").val("").change();
        $("#days").val("").change();
        $('#reportrange span').html('Filter By Date');
        $('#reportrange').val('');
        $("#from_date").val('');
        $("#to_date").val('');

        $('#search_im').val('');
        $('#from_date_im').val('');
        $('#to_date_im').val('');
        $('#access_im').val('');

        var type = $("#type").val();
        var page = 1;
        var query = $('#search').val();
        var from_date = $("#from_date").val();
        var to_date = $("#to_date").val();
        var access = $("#access").val();
        var days = $("#days").val();
        var limit = $("#limit").val();
        var franchise_model = "SMRA";

        $(".franchise-tabs a").removeClass("active");
        $('.franchise-tabs a[title="' + franchise_model + '"]').addClass('active');

        load_data(page,type,query,from_date,to_date,access,limit,franchise_model,days);
    });

    $(document).on('click', '.changeAccess', function(e)
	{
        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
              confirmButton: 'btn btn-success m-10',
              cancelButton: 'btn btn-danger m-10'
            },
            buttonsStyling: false
        })
          
        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes!',
            cancelButtonText: 'No!',
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
                var id = this.id;
                var new_id=id.split("_");
                var table=new_id[2];
                if(new_id.length>2)
                {
                    table_arr=[];
                    for(i=2;i<new_id.length;i++)
                    {
                        table_arr.push(new_id[i])
                    }
                    table=table_arr.join("_")
                }
                $.ajax({
                    url: window.APP_URLS.changeAccess,
                    type: 'POST',
                    data:{
                            changeAccess:'changeAccess',
                            unique_id:new_id[1],
                            _status:new_id[0],
                            table:table,
                            csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
                     }
                })
                .done(function(response)
                {
                    // console.log(response)
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
        
                            load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
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
                        // console.log(error)
                        $.toast({
                            heading: 'Error',
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            position: 'top-right',
                            loaderBg: '#ff6849',
                            icon: 'error',
                            hideAfter: 3500
                        });
                    }
                })
                .fail(function(jqXHR, textStatus, error)
                {
                    // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
                    $.toast({
                        heading: 'Error',
                        text: 'Something went wrong. Please try again later.',
                        position: 'top-right',
                        loaderBg: '#ff6849',
                        icon: 'error',
                        hideAfter: 3500
                    });
                });
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Cancelled',
                ':)',
                'error'
              )

              load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
            }
        })
	});

    $(document).on('click', '.mac_reset', function(e)
	{
        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
              confirmButton: 'btn btn-success m-10',
              cancelButton: 'btn btn-danger m-10'
            },
            buttonsStyling: false
        })
          
        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You wan't to reset the mac!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes!',
            cancelButtonText: 'No!',
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
                var id = this.id;
                $.ajax({
                    url: window.APP_URLS.macReset,
                    type: 'POST',
                    data:{
                        mac_reset:'mac_reset',
                        unique_id:id,
                        csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
                     }
                })
                .done(function(response)
                {
                    // console.log(response)
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
        
                            load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
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
                        // console.log(error)
                        $.toast({
                            heading: 'Error',
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            position: 'top-right',
                            loaderBg: '#ff6849',
                            icon: 'error',
                            hideAfter: 3500
                        });
                    }
                })
                .fail(function(jqXHR, textStatus, error)
                {
                    // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
                    $.toast({
                        heading: 'Error',
                        text: 'Something went wrong. Please try again later.',
                        position: 'top-right',
                        loaderBg: '#ff6849',
                        icon: 'error',
                        hideAfter: 3500
                    });
                });
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Cancelled',
                ':)',
                'error'
              )

              load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
            }
        })
	});

    $(document).on('click', '.updateStatus', function(e)
	{
        let status = $(this).data("status");  // NEW
        let id = $(this).data("id");          // NEW

        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
              confirmButton: 'btn btn-success m-10',
              cancelButton: 'btn btn-danger m-10'
            },
            buttonsStyling: false
        })
          
        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You want to " + status + " this entry?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes!',
            cancelButtonText: 'No!',
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
                var id = this.id;
                $.ajax({
                    url: window.APP_URLS.update_franchise_status,
                    type: 'POST',
                    data:{
                        franchise_id:id,
                        status:status,
                        csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
                     }
                })
                .done(function(response)
                {
                    // console.log(response)
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
        
                            load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
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
                        // console.log(error)
                        $.toast({
                            heading: 'Error',
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            position: 'top-right',
                            loaderBg: '#ff6849',
                            icon: 'error',
                            hideAfter: 3500
                        });
                    }
                })
                .fail(function(jqXHR, textStatus, error)
                {
                    // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
                    $.toast({
                        heading: 'Error',
                        text: 'Something went wrong. Please try again later.',
                        position: 'top-right',
                        loaderBg: '#ff6849',
                        icon: 'error',
                        hideAfter: 3500
                    });
                });
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Cancelled',
                ':)',
                'error'
              )

              load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
            }
        })
	});

    $(document).on('click', '.changeTrade', function(e)
	{
        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
              confirmButton: 'btn btn-success m-10',
              cancelButton: 'btn btn-danger m-10'
            },
            buttonsStyling: false
        })
          
        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes!',
            cancelButtonText: 'No!',
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
                let dataId = $(this).data('id');
                let dataStatus = $(this).data('status');
                // console.log(dataId);
                // console.log(dataStatus);

                $.ajax({
                    url: window.APP_URLS.changeTradingOption,
                    type: 'POST',
                    data:{
                            changeTrade:'changeTrade',
                            unique_id:dataId,
                            trading:dataStatus,
                            csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
                     }
                })
                .done(function(response)
                {
                    // console.log(response)
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
        
                            load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
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
                        // console.log(error)
                        $.toast({
                            heading: 'Error',
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            position: 'top-right',
                            loaderBg: '#ff6849',
                            icon: 'error',
                            hideAfter: 3500
                        });
                    }
                })
                .fail(function(jqXHR, textStatus, error)
                {
                    // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
                    $.toast({
                        heading: 'Error',
                        text: 'Something went wrong. Please try again later.',
                        position: 'top-right',
                        loaderBg: '#ff6849',
                        icon: 'error',
                        hideAfter: 3500
                    });
                });
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Cancelled',
                ':)',
                'error'
              )

              load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
            }
        })
	});

    $(document).on('click', '.updateTradingStatus', function(e)
	{
        let status = $(this).data("status");  // NEW
        let id = $(this).data("id");          // NEW

        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
              confirmButton: 'btn btn-success m-10',
              cancelButton: 'btn btn-danger m-10'
            },
            buttonsStyling: false
        })
          
        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You want to " + status + " this entry?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes!',
            cancelButtonText: 'No!',
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
                var id = this.id;
                $.ajax({
                    url: window.APP_URLS.update_trading_status,
                    type: 'POST',
                    data:{
                        customer_id:id,
                        status:status,
                        csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
                     }
                })
                .done(function(response)
                {
                    // console.log(response)
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
        
                            load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
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
                        // console.log(error)
                        $.toast({
                            heading: 'Error',
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            position: 'top-right',
                            loaderBg: '#ff6849',
                            icon: 'error',
                            hideAfter: 3500
                        });
                    }
                })
                .fail(function(jqXHR, textStatus, error)
                {
                    // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
                    $.toast({
                        heading: 'Error',
                        text: 'Something went wrong. Please try again later.',
                        position: 'top-right',
                        loaderBg: '#ff6849',
                        icon: 'error',
                        hideAfter: 3500
                    });
                });
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Cancelled',
                ':)',
                'error'
              )

              load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
            }
        })
	});

    $(document).on('click', '.updateWithdrawalStatus', function () {

        let status = $(this).data("status");
        let id = $(this).data("id");

        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
                confirmButton: 'btn btn-success m-10',
                cancelButton: 'btn btn-danger m-10'
            },
            buttonsStyling: false
        });

        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You want to " + status + " this withdrawal?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes!',
            cancelButtonText: 'No!',
            reverseButtons: true
        }).then((result) => {

            if (result.isConfirmed) {

                $('#withdraw_id').val(id);
                $('#withdraw_status').val(status);

                $('#txn_number').val('');
                $('#remark').val('');

                // 🔥 show/hide txn field
                if (status === "Approved") {
                    $('#txn_field').show();
                } else {
                    $('#txn_field').hide();
                }

                $('#withdrawModal').modal('show');

            }
            else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Cancelled',
                ':)',
                'error'
              )

              load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
            }
        });
    });

    $('#submitApprove').click(function () 
    {
        let id = $('#withdraw_id').val();
        let status = $('#withdraw_status').val();
        let txn = $('#txn_number').val();
        let remark = $('#remark').val();

        if (status === "Approved" && (!txn || txn.trim() === "")) {
            $.toast({
                heading: 'Error',
                text: "Transaction number required",
                icon: 'error',
                position: 'top-right',
            });
            return;
        }

        if (status === "Rejected" && (!remark || remark.trim() === "")) {
            $.toast({
                heading: 'Error',
                text: "Remark is required",
                icon: 'error',
                position: 'top-right',
            });
            return;
        }

        processWithdrawal(id, status, txn, remark);

        $('#withdrawModal').modal('hide');
    });

    $(document).on('click', '.changeAccountType', function(e)
	{
        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
              confirmButton: 'btn btn-success m-10',
              cancelButton: 'btn btn-danger m-10'
            },
            buttonsStyling: false
        })
          
        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes!',
            cancelButtonText: 'No!',
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
                let dataId = $(this).data('id');
                let dataStatus = $(this).data('status');
                // console.log(dataId);
                // console.log(dataStatus);

                $.ajax({
                    url: window.APP_URLS.changeTradingAccount,
                    type: 'POST',
                    data:{
                            changeAccountType:'changeAccountType',
                            unique_id:dataId,
                            account:dataStatus,
                            csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
                     }
                })
                .done(function(response)
                {
                    // console.log(response)
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
        
                            load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
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
                        // console.log(error)
                        $.toast({
                            heading: 'Error',
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            position: 'top-right',
                            loaderBg: '#ff6849',
                            icon: 'error',
                            hideAfter: 3500
                        });
                    }
                })
                .fail(function(jqXHR, textStatus, error)
                {
                    // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
                    $.toast({
                        heading: 'Error',
                        text: 'Something went wrong. Please try again later.',
                        position: 'top-right',
                        loaderBg: '#ff6849',
                        icon: 'error',
                        hideAfter: 3500
                    });
                });
            } else if (
              /* Read more about handling dismissals below */
              result.dismiss === Swal.DismissReason.cancel
            ) {
              swalWithBootstrapButtons.fire(
                'Cancelled',
                ':)',
                'error'
              )

              load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
            }
        })
	});

    $(document).on("click","#downloadExcel",function(){

        var type = $("#type").length ? $("#type").val() : "";
        var query = $("#search").length ? $("#search").val() : "";
        var from_date = $("#from_date").length ? $("#from_date").val() : "";
        var to_date = $("#to_date").length ? $("#to_date").val() : "";
        var access = $("#access").length ? $("#access").val() : "";
        var days = $("#days").length ? $("#days").val() : "";

        var franchise_model = "SMRA";

        if($(".franchise-tabs a.active").length){
            franchise_model = $(".franchise-tabs a.active").attr("title");
        }

        var form = $('<form method="POST" action="'+window.APP_URLS.exportData+'"></form>');

        form.append('<input type="hidden" name="csrfmiddlewaretoken" value="'+$("input[name=csrfmiddlewaretoken]").val()+'">');
        form.append('<input type="hidden" name="type" value="'+type+'">');
        form.append('<input type="hidden" name="query" value="'+query+'">');
        form.append('<input type="hidden" name="from_date" value="'+from_date+'">');
        form.append('<input type="hidden" name="to_date" value="'+to_date+'">');
        form.append('<input type="hidden" name="access" value="'+access+'">');
        form.append('<input type="hidden" name="days" value="'+days+'">');
        form.append('<input type="hidden" name="franchise_model" value="'+franchise_model+'">');
        form.append('<input type="hidden" name="export" value="excel">');
        $("body").append(form);
        form.submit();
    });
});

var franchise_model = "SMRA";
function load_data(page,type,query='',from_date='',to_date='',access='',limit='',fm=franchise_model, days='')
{
    // showModal();
    $.ajax({
        url:window.APP_URLS.getAllDataByTable,
        method:"POST",
        data:{page:page, query:query,type:type,from_date:from_date,to_date:to_date,access:access,limit:limit,franchise_model:fm,days:days,csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
        success:function(data)
        {
            // console.log(data)
            // hideModal();
            $('.dynamic_content').html('');
            $(".pagination").html('');
            
            if(data.table_data.length>0)
            {
                if(type=="metal_purity_price")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].metal+'</td>\
                                <td>'+data.table_data[i].purity+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].price+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                                <td>\
                                    <label class="switch" title="Toggle Access">\
                                        <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>\
                                <td>\
                                    <button data-toggle="modal" data-target="#edit-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-primary edit'+type+'" title="Edit Details"><span class="fa fa-pencil-square-o"></span></button>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="unit")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].unit_name+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                                <td>\
                                    <label class="switch" title="Toggle Access">\
                                        <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>\
                                <td>\
                                    <button data-toggle="modal" data-target="#edit-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-primary edit'+type+'" title="Edit Details"><span class="fa fa-pencil-square-o"></span></button>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="category")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td><img height="50px" src="'+data.table_data[i].image+'"></td>\
                                <td>'+data.table_data[i].name+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                                <td>\
                                    <label class="switch" title="Toggle Access">\
                                        <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>\
                                <td>\
                                    <button data-toggle="modal" data-target="#edit-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-primary edit'+type+'" title="Edit Details"><span class="fa fa-pencil-square-o"></span></button>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="product")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].name+'</td>\
                                <td>'+data.table_data[i].category+'</td>\
                                <td>'+data.table_data[i].size+'</td>\
                                <td>'+data.table_data[i].metal+'</td>\
                                <td>'+data.table_data[i].metal_type+'</td>\
                                <td>'+data.table_data[i].purity+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].price+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].hot_cls+'">'+data.table_data[i].hot_sale+'</span></td>\
                                <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                                <td>\
                                    <label class="switch" title="Toggle Access">\
                                        <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>\
                                <td>\
                                    <a href="update-product?id='+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-primary title="Edit Details"><span class="fa fa-pencil-square-o"></span></a>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="customer")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td>'+data.table_data[i].email+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                                <td>\
                                    <label class="switch" title="Toggle Access">\
                                        <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>\
                                <td>\
                                    <button data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-warning mac_reset" title="Mac Reset"><span class="fa fa-refresh"></span></button>\
                                </td>\
                                <td>'+data.table_data[i].mac_reset_count+'</td>\
                                <td>\
                                    <button data-toggle="modal" data-target="#view-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-info view'+type+'" title="View Details"><span class="fa fa-eye"></span></button>\
                                </td>\
                                <td>\
                                    <button onclick="openEditCustomerModal(\''+data.table_data[i].unique_id+'\')" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-warning" title="Edit Customer"><span class="fa fa-pencil"></span></button>\
                                </td>\
                                <td><span class="badge badge-'+data.table_data[i].cls_trade+'">'+data.table_data[i].trading+'</span></td>\
                                <td>\
                                    <label class="switch" title="Toggle Trading">\
                                        <input type="checkbox" value="'+data.table_data[i].trading+'" class="changeTrade" data-id="'+data.table_data[i].unique_id+'" data-status="'+data.table_data[i].trading+'" '+data.table_data[i].states_trade+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>\
                                <td>\
                                    <button data-toggle="modal" data-target="#trading-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-info view_trading" title="View Trading Details"><span class="fa fa-inr"></span></button>\
                                </td>';
                            if(data.table_data[i].btn == 'Yes')
                            {
                                output+='\
                                    <td>\
                                        <button data-id="'+data.table_data[i].unique_id+'" data-status="Approved" id="'+data.table_data[i].unique_id+'" class="btn btn-social-icon btn-success updateTradingStatus" title="Approve Status"><span class="fa fa-check"></span> Approve</button>\
                                        <button data-id="'+data.table_data[i].unique_id+'" data-status="Rejected" id="'+data.table_data[i].unique_id+'" class="btn btn-social-icon btn-danger updateTradingStatus" title="Reject Status"><span class="fa fa-times"></span> Reject</button>\
                                    </td>';
                            }
                            else
                            {
                                output+='<td><span class="badge badge-'+data.table_data[i].status_cls+'">'+data.table_data[i].status_txt+'</span></td>';
                            }
                            if(data.table_data[i].demo_account == 'N/A')
                            {
                                output+='<td><span class="badge badge-'+data.table_data[i].cls_account+'">'+data.table_data[i].demo_account+'</span></td>';
                            }
                            else
                            {
                                output+='\
                                <td>\
                                    <label class="switch" title="Toggle Account Type">\
                                        <input type="checkbox" value="'+data.table_data[i].demo_account+'" class="changeAccountType" data-id="'+data.table_data[i].unique_id+'" data-status="'+data.table_data[i].demo_account+'" '+data.table_data[i].states_account+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>';
                            }
                            output+='\
                                <td>\
                                    <button data-toggle="modal" data-target="#transfer-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-primary transfer_referral" title="Transfer Referral"><span class="mdi mdi-account-network"></span></button>\
                                </td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="image_slider")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].image_type+'</td>\
                                <td><img src="'+data.table_data[i].image+'" width="50px"></td>\
                                <td>'+data.table_data[i].sequence+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                                <td>\
                                    <label class="switch" title="Toggle Access">\
                                        <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                        <span class="slider round"></span>\
                                    </label>\
                                </td>\
                                <td>\
                                    <button data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-danger delete'+type+'" title="Delete Details"><span class="fa fa-trash"></span></button>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="customer_cart_list")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td><strong><span class="text text-primary">'+data.table_data[i].total_items+'</span></strong></td>\
                                <td><strong><span class="text text-danger">'+data.table_data[i].total_quantity+'</span></strong></td>\
                                <td><strong><span class="text text-success"><i class="fa fa-inr"></i> '+data.table_data[i].cart_value+'</span></strong></td>\
                                <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].cart_status+'</span></td>\
                                <td>\
                                    <button data-toggle="modal" data-target="#view-modal" data-id="'+data.table_data[i].cart_id+'" id="'+data.table_data[i].cart_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-info view'+type+'" title="View Details"><span class="fa fa-eye"></span></button>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="customer_order_list")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].order_number+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td><strong><span class="text text-primary">'+data.table_data[i].total_items+'</span></strong></td>\
                                <td><strong><span class="text text-danger">'+data.table_data[i].total_quantity+'</span></strong></td>\
                                <td><strong><span class="text text-success"><i class="fa fa-inr"></i> '+data.table_data[i].sub_total+'</span></strong></td>\
                                <!--<td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].order_status+'</span></td>-->\
                                <td>'+data.table_data[i].razorpay_order_id+'</td>\
                                <td>'+data.table_data[i].razorpay_payment_id+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].pay_cls+'">'+data.table_data[i].payment_status+'</span></td>\
                                <td>\
                                    <button data-toggle="modal" data-target="#view-modal" data-id="'+data.table_data[i].order_id+'" id="'+data.table_data[i].order_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-info view'+type+'" title="View Details"><span class="fa fa-eye"></span></button>\
                                    <a href="'+data.table_data[i].invoice_url+'" target="_blank" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-warning" title="View Invoice"><span class="fa fa-file-pdf-o"></span></a>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="stock")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].product_name+'</td>\
                                <td>'+data.table_data[i].quantity+'</td>\
                                <td>'+data.table_data[i].last_updated+'</td>\
                                <td>\
                                    <!--<a href="stock-movement/'+data.table_data[i].product+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-info" title="View Stock Movement"><span class="fa fa-eye"></span></a>-->\
                                    <a href="#" class="stock-movement-link waves-effect waves-circle btn btn-social-icon btn-circle btn-info" data-product-id="'+data.table_data[i].product+'" title="View Stock Movement"><span class="fa fa-eye"></span></a>\
                                </td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="stock_movement")
                {
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        $('.dynamic_content').append('\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].product_name+'</td>\
                                <td>'+data.table_data[i].movement_type+'</td>\
                                <td>'+data.table_data[i].quantity+'</td>\
                                <td>'+data.table_data[i].reference+'</td>\
                                <td>'+data.table_data[i].movement_date+'</td>\
                            </tr>\
                        ');
                    }
                }
                else if(type=="trading_user")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='<tr>\
                            <td>'+data.table_data[i].sr_no+'</td>\
                            <td>'+data.table_data[i].date+'</td>\
                            <td>'+data.table_data[i].franchise_name+'</td>\
                            <td>'+data.table_data[i].holder_name+'</td>\
                            <td>'+data.table_data[i].referral_id+'</td>\
                            <td>'+data.table_data[i].mobile+'</td>\
                            <td>'+data.table_data[i].email+'</td>\
                            <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                            <td>\
                                <label class="switch" title="Toggle Access">\
                                    <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                    <span class="slider round"></span>\
                                </label>\
                            </td>\
                            <td>\
                                <button data-toggle="modal" data-target="#view-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-info view'+type+'" title="View Details"><span class="fa fa-eye"></span></button>';
                                if(data.table_data[i].roleAccess)
                                {
                                    output += '<button data-toggle="modal" data-target="#view-franchise-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-warning viewHierarchy" title="View Hierarchy"><span class="mdi mdi-account-network"></span></button>';
                                }
                            output += '</td>';
                        if(data.table_data[i].btn == 'Yes' && data.table_data[i].roleAccess)
                        {
                            output+='\
                                <td>\
                                    <button data-id="'+data.table_data[i].unique_id+'" data-status="Approved" id="'+data.table_data[i].unique_id+'" class="btn btn-social-icon btn-success updateStatus" title="Approve Status"><span class="fa fa-check"></span> Approve</button>\
                                    <button data-id="'+data.table_data[i].unique_id+'" data-status="Rejected" id="'+data.table_data[i].unique_id+'" class="btn btn-social-icon btn-danger updateStatus" title="Reject Status"><span class="fa fa-times"></span> Reject</button>\
                                </td>';
                        }
                        else
                        {
                            output+='<td><span class="badge badge-'+data.table_data[i].status_cls+'">'+data.table_data[i].status+'</span></td>';
                        }
                        output+='</tr>';
                        
                    }

                    $('.dynamic_content').append(output);
                }
                else if(type=="contact_messages")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='<tr>\
                            <td>'+data.table_data[i].sr_no+'</td>\
                            <td>'+data.table_data[i].date+'</td>\
                            <td>'+data.table_data[i].name+'</td>\
                            <td>'+data.table_data[i].phone+'</td>\
                            <td>'+data.table_data[i].email+'</td>\
                            <td>'+data.table_data[i].message+'</td>\
                        </tr>';
                    }

                    $('.dynamic_content').append(output);
                }
                else if(type=="portal_user")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output+='\
                        <tr>\
                            <td>'+data.table_data[i].sr_no+'</td>\
                            <td>'+data.table_data[i].date+'</td>\
                            <td>'+data.table_data[i].name+'</td>\
                            <td>'+data.table_data[i].mobile_number+'</td>\
                            <td>'+data.table_data[i].email+'</td>\
                            <td>'+data.table_data[i].password+'</td>\
                            <!--<td>'+data.table_data[i].role+'</td>-->\
                            <td><span class="badge badge-'+data.table_data[i].cls+'">'+data.table_data[i].access+'</span></td>\
                            <td>\
                                <label class="switch" title="Toggle Access">\
                                    <input type="checkbox" value="'+data.table_data[i].access+'" class="changeAccess" id="'+data.table_data[i].access+'_'+data.table_data[i].unique_id+'_'+type+'" '+data.table_data[i].states+'/>\
                                    <span class="slider round"></span>\
                                </label>\
                            </td>\
                            <td>\
                                <button data-toggle="modal" data-target="#edit-modal" data-id="'+data.table_data[i].unique_id+'" id="'+data.table_data[i].unique_id+'" class="waves-effect waves-circle btn btn-social-icon btn-circle btn-primary edit'+type+'" title="Edit Details"><span class="fa fa-pencil-square-o"></span></button>\
                            </td>\
                        </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="registration_report")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td>'+data.table_data[i].state+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].last_login+'</td>\
                                <td>'+data.table_data[i].latitude+'</td>\
                                <td>'+data.table_data[i].longitude+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="wallet_recharge_report" || type=="first_recharge_report")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].amount+'</td>\
                                <td>'+data.table_data[i].transaction_date+'</td>\
                                <td>'+data.table_data[i].membership+'</td>\
                                <td>'+data.table_data[i].razorpay_order_id+'</td>\
                                <td>'+data.table_data[i].razorpay_payment_id+'</td>\
                                <td>'+data.table_data[i].status+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="transaction_report")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td>'+data.table_data[i].metal_type+'</td>\
                                <td>'+data.table_data[i].quantity+'</td>\
                                <td>'+data.table_data[i].invested_amount+'</td>\
                                <td>'+data.table_data[i].buy_price+'</td>\
                                <td>'+data.table_data[i].buy_date+'</td>\
                                <td>'+data.table_data[i].sell_price+'</td>\
                                <td>'+data.table_data[i].sell_date+'</td>\
                                <td>'+data.table_data[i].order_type+'</td>\
                                <td>'+data.table_data[i].profit_loss+'</td>\
                                <td>'+data.table_data[i].pnl_amount+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="customer_report")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td>'+data.table_data[i].email+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td>'+data.table_data[i].aadhaar_number+'</td>\
                                <td>'+data.table_data[i].pan_number+'</td>\
                                <td>'+data.table_data[i].addresses+'</td>\
                                <td>'+data.table_data[i].access+'</td>\
                                <td>'+data.table_data[i].trading+'</td>\
                                <td>'+data.table_data[i].trading_status+'</td>\
                                <td>'+data.table_data[i].account_type+'</td>\
                                <td>'+data.table_data[i].bank_name+'</td>\
                                <td>'+data.table_data[i].account_holder_name+'</td>\
                                <td>'+data.table_data[i].account_number+'</td>\
                                <td>'+data.table_data[i].ifsc_code+'</td>\
                                <td>'+data.table_data[i].branch_name+'</td>\
                                <td>'+data.table_data[i].documents+'</td>\
                                <td>'+data.table_data[i].last_login+'</td>\
                                <td>'+data.table_data[i].latitude+'</td>\
                                <td>'+data.table_data[i].longitude+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="order_report")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].order_date+'</td>\
                                <td>'+data.table_data[i].order_number+'</td>\
                                <td>'+data.table_data[i].order_id+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile+'</td>\
                                <td>'+data.table_data[i].email+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td>'+data.table_data[i].product_detail_id+'</td>\
                                <td>'+data.table_data[i].product_name+'</td>\
                                <td>'+data.table_data[i].category+'</td>\
                                <td>'+data.table_data[i].quantity+'</td>\
                                <td>'+data.table_data[i].price+'</td>\
                                <td>'+data.table_data[i].total+'</td>\
                                <td>'+data.table_data[i].total_items+'</td>\
                                <td>'+data.table_data[i].total_quantity+'</td>\
                                <td>'+data.table_data[i].sub_total+'</td>\
                                <td>'+data.table_data[i].product_status+'</td>\
                                <td>'+data.table_data[i].status_history+'</td>\
                                <td>'+data.table_data[i].remark+'</td>\
                                <td>'+data.table_data[i].razorpay_order_id+'</td>\
                                <td>'+data.table_data[i].razorpay_payment_id+'</td>\
                                <td>'+data.table_data[i].payment_status+'</td>\
                                <td>'+data.table_data[i].address_name+'</td>\
                                <td>'+data.table_data[i].address_mobile+'</td>\
                                <td>'+data.table_data[i].pincode+'</td>\
                                <td>'+data.table_data[i].postoffice+'</td>\
                                <td>'+data.table_data[i].state+'</td>\
                                <td>'+data.table_data[i].city+'</td>\
                                <td>'+data.table_data[i].district+'</td>\
                                <td>'+data.table_data[i].region+'</td>\
                                <td>'+data.table_data[i].address_line_1+'</td>\
                                <td>'+data.table_data[i].address_line_2+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="inactive_no_recharge")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile+'</td>\
                                <td>'+data.table_data[i].email+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td>'+data.table_data[i].trading+'</td>\
                                <td>'+data.table_data[i].status+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="inactive_customers")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile+'</td>\
                                <td>'+data.table_data[i].email+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td>'+data.table_data[i].last_login+'</td>\
                                <td>'+data.table_data[i].last_transaction+'</td>\
                                <td>'+data.table_data[i].days_inactive+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="customer_transfer_report")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].old_referral_code+'</td>\
                                <td>'+data.table_data[i].new_referral_code+'</td>\
                                <td>'+data.table_data[i].transfer_date+'</td>\
                                <td>'+data.table_data[i].reason_for_transfer+'</td>\
                            </tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                else if(type=="withdrawal_report")
                {
                    output = '';
                    for(var i=0;i<data.table_data.length;i++)
                    {
                        output +='\
                            <tr>\
                                <td>'+data.table_data[i].sr_no+'</td>\
                                <td>'+data.table_data[i].customer_name+'</td>\
                                <td>'+data.table_data[i].mobile_number+'</td>\
                                <td>'+data.table_data[i].date+'</td>\
                                <td>'+data.table_data[i].referral_code+'</td>\
                                <td>'+data.table_data[i].referral_holder_name+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].request_amount+'</td>\
                                <td>'+data.table_data[i].request_date+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].service_charge+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].gst_amount+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].total_deduction+'</td>\
                                <td><i class="fa fa-inr"></i> '+data.table_data[i].final_amount+'</td>\
                                <td><span class="badge badge-'+data.table_data[i].status_cls+'">'+data.table_data[i].status+'</span></td>\
                                <td>'+data.table_data[i].action_date+'</td>\
                                <td>'+data.table_data[i].transaction_number+'</td>\
                                <td>'+data.table_data[i].remark+'</td>\
                                <td>'+data.table_data[i].account_holder_name+'</td>\
                                <td>'+data.table_data[i].account_number+'</td>\
                                <td>'+data.table_data[i].ifsc_code+'</td>\
                                <td>'+data.table_data[i].bank_name+'</td>';
                                if(data.table_data[i].btn == 'Yes')
                                {
                                    output+='\
                                        <td>\
                                            <button data-id="'+data.table_data[i].unique_id+'" data-status="Approved" id="'+data.table_data[i].unique_id+'" class="btn btn-social-icon btn-success updateWithdrawalStatus" title="Approve Status"><span class="fa fa-check"></span> Approve</button>\
                                            <button data-id="'+data.table_data[i].unique_id+'" data-status="Rejected" id="'+data.table_data[i].unique_id+'" class="btn btn-social-icon btn-danger updateWithdrawalStatus" title="Reject Status"><span class="fa fa-times"></span> Reject</button>\
                                        </td>';
                                }
                                else
                                {
                                    output+='<td></td>';
                                }
                            output+='</tr>';
                    }
                    $('.dynamic_content').append(output);
                }
                
                $(".no-data").css("display","none");
                $(".table-bot").css("display","flex");
                $(".show_p").html("Showing <strong>"+data.total_filter_data+"</strong> of <strong>"+data.total_data+"</strong> records")
            }
            else
            {
                $(".table-bot").css("display","none");
                $(".no-data").css("display","block");
            }

            if(data.page_array.length>1)
            {
                page_array=data.page_array;
                page_link="";
                previous_link="";
                next_link="";
                for(count = 0; count < page_array.length; count++)
                {
                    if(page == page_array[count])
                    {
                        page_link += '\
                        <li class="page-item active">\
                            <a class="page-link" href="#" data-page_number="'+page_array[count]+'">'+page_array[count]+' <span class="sr-only">\(current)</span></a>\
                        </li>';

                        previous_id = page_array[count] - 1;
                        if(previous_id > 0)
                        {
                            previous_link = '<li class="page-item"><a class="page-link" href="javascript:void(0)" data-page_number="'+previous_id+'">Previous</a></li>';
                        }
                        else
                        {
                            previous_link = '\
                            <li class="page-item disabled">\
                                <a class="page-link" href="#">Previous</a>\
                            </li>';
                        }

                        next_id = page_array[count] + 1;
                        if(next_id > data.total_links)
                        {
                            next_link = '\
                            <li class="page-item disabled">\
                                <a class="page-link" href="#">Next</a>\
                            </li>';
                        }
                        else
                        {
                            next_link = '<li class="page-item"><a class="page-link" href="javascript:void(0)" data-page_number="'+next_id+'">Next</a></li>';
                        }
                    }
                    else
                    {
                        if(page_array[count] == '...')
                        {
                            page_link += '\
                            <li class="page-item disabled">\
                                <a class="page-link" href="#">...</a>\
                            </li>';
                        }
                        else
                        {
                            page_link += '<li class="page-item"><a class="page-link" href="javascript:void(0)" data-page_number="'+page_array[count]+'">'+page_array[count]+'</a></li>';
                        }
                    }
                }

                $(".pagination").html(previous_link+page_link+next_link);
            }
        },
        error: function(jqXHR, textStatus, error) 
        {
            // hideModal();
            // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
            $.toast({
                heading: 'Error',
                text: 'Error loading data. Please try again later.',
                position: 'top-right',
                loaderBg: '#ff6849',
                icon: 'error',
                hideAfter: 3500
            });
        }
    });
}

function processWithdrawal(id, status, txn, remark) {

    $.ajax({
        url: window.APP_URLS.update_withdrawal_status,
        type: 'POST',
        data: {
            unique_id: id,
            status: status,
            transaction_number: txn,
            remark: remark,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function (response) {
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

                    load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
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
                // console.log(error)
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
        error:function(jqXHR, textStatus, error)
        {
            // console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
            $.toast({
                heading: 'Error',
                text: 'Something went wrong. Please try again later.',
                position: 'top-right',
                loaderBg: '#ff6849',
                icon: 'error',
                hideAfter: 3500
            });
        }
    });
}