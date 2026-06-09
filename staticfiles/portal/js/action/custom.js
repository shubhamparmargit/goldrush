$(document).ready(function(){
	$(document).on('click', '.editmetal_purity_price', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		$('#modal-loader').show();
		$.ajax({
			url: window.APP_URLS.getPurityPrice,
			type: 'POST',
			data:
			{
				metal_purity_price:'metal_purity_price',
				unique_id:uid,
				csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data)
		{
			// console.log(data)
			try
            {
				$('#modal-loader').hide();	
				if(data.success==1)
				{
					$("#price_id").val(data.unique_id);
					$("#purity_id").val(data.purity_id);
					$("#metal_e").val(data.metal_id).trigger('change');
					$("#purity_e").val(data.purity_id).trigger('change');
					$("#price_e").val(data.price);
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
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.editunit', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		$('#modal-loader').show();
		$.ajax({
			url: window.APP_URLS.getUnit,
			type: 'POST',
			data:
			{
				unit:'unit',
				unique_id:uid,
				csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data)
		{
			// console.log(data)
			try
            {
				$('#modal-loader').hide();	
				if(data.success==1)
				{
					$("#unit_id").val(data.unique_id);
					$("#unit_e").val(data.unit_name);
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
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.editcategory', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		$('#modal-loader').show();
		$.ajax({
			url: window.APP_URLS.getCategory,
			type: 'POST',
			data:
			{
				category:'category',
				unique_id:uid,
				csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data)
		{
			// console.log(data)
			try
            {
				$('#modal-loader').hide();	
				if(data.success==1)
				{
					$("#category_id").val(data.unique_id);
					$("#name_e").val(data.name);
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
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.viewcustomer', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		$('#modal-loader').show();
		$.ajax({
			url: window.APP_URLS.getCustomer,
			type: 'POST',
			data:
			{
				customer:'customer',
				unique_id:uid,
				csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data)
		{
			// console.log(data)
			$('#modal-loader').hide();	
			if(data[0].success==1)
			{
				$('#date_v').html(data[0].register_date_time);
				$('#person_v').html(data[0].name);
				$('#mobile_v').html(data[0].mobile);
				$('#email_v').html(data[0].email);
				$('#referral_code_v').html(data[0].referral_code);
				$('#aadhaar_number_v').html(data[0].aadhaar_number);
				$('#aadhaar_front_v').html(data[0].aadhaar_front_image);
				$("#aadhaar_front_v").attr("href",data[0].aadhaar_front_image);
				$('#aadhaar_back_v').html(data[0].aadhaar_back_image);
				$('#aadhaar_back_v').attr("href",data[0].aadhaar_back_image);
				$('#pan_number_v').html(data[0].pan_number);
				$('#pan_front_v').html(data[0].pan_front_image);
				$("#pan_front_v").attr("href",data[0].pan_front_image);

				getAllVendorAddress(data[0].address_details);
			}
		})
		.fail(function(jqXHR, textStatus, error)
		{
			// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.deleteimage_slider', function(e)
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
                $.ajax({
                    url: window.APP_URLS.deleteImage,
                    type: 'POST',
                    data:{
						image_slider:'image_slider',
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
	$(document).on('click', '.viewcustomer_cart_list', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		$('#modal-loader').show();
		$.ajax({
			url: window.APP_URLS.getCustomerCartDetails,
			type: 'POST',
			data:
			{
				customer_cart_list:'customer_cart_list',
				cart_id:uid,
				csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data)
		{
			// console.log(data)
			$('#modal-loader').hide();	
			if(data.success==1)
			{
				$('#date_v').html(data.cart_date);
				$('#status_v').html('<span class="badge badge-'+data.cls+'">'+data.cart_status+'</span>');
				$('#name_v').html(data.customer_name);
				$('#mobile_v').html(data.customer_mobile);
				$('#email_v').html(data.customer_email);

				output='';
				if(data.cart_details.length>0)
				{
					output+='\
						<div class="table-responsive">\
							<table class="table table-bordered table-striped table-actions">\
								<tr>\
									<th colspan="9" style="text-align:center">Product Details</th>\
								</tr>\
								<tr>\
									<th>Added On</th>\
									<th>Category</th>\
									<th>Product Name</th>\
									<th>Photo</th>\
									<th>Quantity</th>\
									<th>Price</th>\
									<th>Total</th>\
								</tr>\
					';
					for(var i=0;i<data.cart_details.length;i++)
					{
						output+='\
							<tr>\
								<td>'+data.cart_details[i].date+'</td>\
								<td>'+data.cart_details[i].category+'</td>\
								<td>'+data.cart_details[i].name+'</td>\
								<td><img src="'+data.cart_details[i].image+'" height="100px"></td>\
								<td>'+data.cart_details[i].quantity+'</td>\
								<td>'+data.cart_details[i].price+'</td>\
								<td>'+data.cart_details[i].total+'</td>\
							</tr>\
						';
					}
					output+='\
							</table>\
						</div>\
					';
				}
				$('.product_details').html(output);
			}
		})
		.fail(function(jqXHR, textStatus, error)
		{
			// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.viewcustomer_order_list', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		getCustomerOrderDetails(uid);
	});	
	$(document).on('click', '.viewtrading_user', function(e){
		e.preventDefault();

		var uid = this.id;
		$('#modal-loader').show();

		$.ajax({
			url: window.APP_URLS.getUser,
			type: 'POST',
			data:{
				trading_user: 'trading_user',
				unique_id: uid,
				csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data){
			// console.log(data);
			$('#modal-loader').hide();

			if(data.success == 1)
			{
				/* ---------- Franchise Basic ---------- */
				$('#date_v').html(data.register_date_time);
				$('#parent_v').html(data.parent_name ? data.parent_name + ' (' + data.parent_referral_id + ')' : 'ROOT');
				$('#model_v').html(data.franchise_model);

				$('#name_v').html(data.franchise_name);
				$('#holder_v').html(data.holder_name);
				$('#access_v').html(data.access);

				/* ---------- Contact ---------- */
				$('#mobile_v').html(data.mobile);
				$('#email_v').html(data.email);
				$('#address_v').html(data.address);

				/* ---------- Identity ---------- */
				$('#company_id_v').html(data.company_support_id);
				$('#referral_v').html(data.referral_id);
				$('#agent_id_v').html(data.agent_id);

				$('#aadhaar_v').html(data.aadhaar_number);
				$('#pan_v').html(data.pan_number);
				$('#gst_v').html(data.gst_number);

				/* ---------- Commission ---------- */
				$('#com_slab_v').html(data.commission_slab);
				$('#com_per_v').html(data.commission_percentage);

				/* ---------- Bank + Docs ---------- */
				if(data.franchiseDetails)
				{
					if(data.franchiseDetails.bank_details)
						getFranchiseBankDetails(data.franchiseDetails.bank_details);

					if(data.franchiseDetails.documents)
						getFranchiseDocuments(data.franchiseDetails.documents);
				}
			}
		})
		.fail(function(jqXHR, textStatus, error){
			// console.log(jqXHR.responseText+" | "+textStatus+" | "+error);
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.viewHierarchy', function(e){
		e.preventDefault();

		var uid = this.id;
		$('#modal-loader').show();

		$.ajax({
			url: window.APP_URLS.franchise_hierarchy,
			type: 'POST',
			data:{
				franchise_id: uid,
				csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(res){
			// console.log(res);
			$('#modal-loader').hide();
            resetHierarchy();
			if (res.status) {
                $("#hierarchyTree").html(renderNode(res.data));
            } else {
                $("#hierarchyTree").html(
                    `<p class="text-danger">${res.msg}</p>`
                );
            }

		})
		.fail(function(jqXHR, textStatus, error){
			// console.log(jqXHR.responseText+" | "+textStatus+" | "+error);
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.view_trading', function(e){
		e.preventDefault();

		var uid = this.id;
		$('#modal-loader').show();

		$.ajax({
			url: window.APP_URLS.getTradingDetails,
			type: 'POST',
			data:{
				trading_details: 'trading_details',
				unique_id: uid,
				csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data){
			// console.log(data);
			$('#modal-loader').hide();

			if(data.success == 1)
			{
				/* ---------- Bank + Docs ---------- */
				if(data.tradingDetails)
				{
					if(data.tradingDetails.bank_details)
						getTradingBankDetails(data.tradingDetails.bank_details);

					if(data.tradingDetails.documents)
						getTradingDocuments(data.tradingDetails.documents);
				}
			}
		})
		.fail(function(jqXHR, textStatus, error){
			// console.log(jqXHR.responseText+" | "+textStatus+" | "+error);
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.editportal_user', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		$('#modal-loader').show();
		$.ajax({
			url: window.APP_URLS.getPortalUser,
			type: 'POST',
			data:
			{
				portal_user:'portal_user',
				unique_id:uid,
				csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
			},
			dataType: 'json'
		})
		.done(function(data)
		{
			// console.log(data);
			try
            {
				$('#modal-loader').hide();	
				if(data.success==1)
				{
					$('#user_id').val(data.unique_id);
					$('#name_e').val(data.name);
					$('#mobile_number_e').val(data.mobile_number);
					$('#email_e').val(data.email);
					$('#password_e').val(data.password);
					// $('#role_e').val(data.role).change();
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
			$('#modal-loader').hide();
		});
	});
	$(document).on('click', '.transfer_referral', function(e)
	{
		e.preventDefault();
		var uid = this.id;
		$('#customer_id').val(uid);
	});
});

function getAllVendorAddress(address_details)
{
	$('.customer_address_details').html('');
	var type="customer_address";
	var output='\
		<div class="row mb-10">\
			<div class="col-md-12">\
				<h4 class="modal-title">Customer Address Details</h4>\
			</div>\
		</div>';
	if(address_details.length>0)
	{
		output+='\
			<div class="table-responsive">\
				<table class="table table-bordered table-striped table-actions">\
					<tr>\
						<th>Sr. no.</th>\
						<th>Activation Date</th>\
						<th>Name</th>\
						<th>Mobile</th>\
						<th>Pincode</th>\
						<th>Postoffice</th>\
						<th>City</th>\
						<th>State</th>\
						<th>District</th>\
						<th>Region</th>\
						<th>Address Line 1</th>\
						<th>Address Line 2</th>\
					</tr>\
		';
		for(var i=0;i<address_details.length;i++)
		{
			output+='\
				<tr>\
					<td>'+address_details[i].sr_no+'</td>\
					<td>'+address_details[i].date+'</td>\
					<td>'+address_details[i].name+'</td>\
					<td>'+address_details[i].mobile+'</td>\
					<td>'+address_details[i].pincode+'</td>\
					<td>'+address_details[i].postoffice+'</td>\
					<td>'+address_details[i].city+'</td>\
					<td>'+address_details[i].state+'</td>\
					<td>'+address_details[i].district+'</td>\
					<td>'+address_details[i].region+'</td>\
					<td>'+address_details[i].address_line_1+'</td>\
					<td>'+address_details[i].address_line_2+'</td>\
				</tr>\
			';
		}
		output+='\
				</table>\
			</div>\
		';
	}
	$('.customer_address_details').html(output);
}

function getCustomerOrderDetails(uid)
{
	$('#modal-loader').show();
	$.ajax({
		url: window.APP_URLS.getCustomerOrderDetails,
		type: 'POST',
		data:
		{
			customer_order_list:'customer_order_list',
			order_id:uid,
			csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
		},
		dataType: 'json'
	})
	.done(function(data)
	{
		// console.log(data)
		$('#modal-loader').hide();	
		if(data[0].success==1)
		{
			$('#date_v').html(data[0].order_date_time);
			$('#id_v').html(data[0].order_id);
			$('#num_v').html(data[0].order_number);
			$('#status_v').html('<span class="badge badge-'+data[0].cls+'">'+data[0].order_status+'</span>');
			$('#razor_id_v').html(data[0].razorpay_order_id);
			$('#razor_payment_v').html(data[0].razorpay_payment_id);
			$('#pay_status_v').html('<span class="badge badge-'+data[0].pay_cls+'">'+data[0].payment_status+'</span>');
			$('#remark_v').html(data[0].remark);
			$('#items_v').html(data[0].total_items);
			$('#quantity_v').html(data[0].total_quantity);
			$('#total_v').html('<span class="fa fa-inr"></span> '+data[0].sub_total);
			$("#invoice_v").attr("href",data[0].invoice_url);
			$('#name_v').html(data[0].customer_name);
			$('#mobile_v').html(data[0].customer_mobile);
			$('#email_v').html(data[0].customer_email);
			$('#add_name_v').html(data[0].address_name);
			$('#add_mobile_v').html(data[0].address_mobile);
			$('#pincode_v').html(data[0].pincode);
			$('#postoffice_v').html(data[0].postoffice);
			$('#city_v').html(data[0].city);
			$('#state_v').html(data[0].state);
			$('#district_v').html(data[0].district);
			$('#region_v').html(data[0].region);
			$('#address_1_v').html(data[0].address_line_1);
			$('#address_2_v').html(data[0].address_line_2);

			output='';
			if(data[0].order_details.length>0)
			{
				output+='\
					<div class="table-responsive">\
						<table class="table table-bordered table-striped table-actions">\
							<tr>\
								<th colspan="5" style="text-align:center">Order Product Details</th>\
								<th colspan="3" style="text-align:right"><button type="button" name="btn_updateProdStatus" id="btn_updateProdStatus" data-id="'+uid+'" class="btn btn-primary pull-right">Update Product Status</button></th>\
							</tr>\
							<tr>\
								<th><input type="checkbox" id="select_all"/><label for="select_all"></label></th>\
								<th>Product Detail Id</th>\
								<th>Category</th>\
								<th>Product Name</th>\
								<th>Quantity</th>\
								<th>Price</th>\
								<th>Total</th>\
								<th>Status</th>\
							</tr>\
				';
				for(var i=0;i<data[0].order_details.length;i++)
				{
					output+='<tr>\
						<td><input type="checkbox" id="'+data[0].order_details[i].product_detail_id+'" name="product_ids" value="'+data[0].order_details[i].product_detail_id+'" class="check"/><label for="'+data[0].order_details[i].product_detail_id+'"></label></td>\
						<td>'+data[0].order_details[i].product_detail_id+'</td>\
						<td>'+data[0].order_details[i].category_name+'</td>\
						<td>'+data[0].order_details[i].product_name+'</td>\
						<td>'+data[0].order_details[i].quantity+'</td>\
						<td><span class="fa fa-inr"></span> '+data[0].order_details[i].price+'</td>\
						<td><span class="fa fa-inr"></span> '+data[0].order_details[i].total+'</td>\
						<td><span class="badge badge-'+data[0].order_details[i].cls1+'">'+data[0].order_details[i].order_status+'</span></td>\
					</tr>\
					';
				}
				output+='\
						</table>\
					</div>\
				';
			}
			$('.product_details').html(output);

			output1='';
			if(data[0].prod_order_status.length>0)
			{
				output1+='\
					<div class="table-responsive">\
						<table class="table table-bordered table-striped table-actions">\
							<tr>\
								<th colspan="8" style="text-align:center">Status Details</th>\
							</tr>\
							<tr>\
								<th>Order Status</th>\
								<th>Status Date & Time</th>\
							</tr>\
				';
				for(var i=0;i<data[0].prod_order_status.length;i++)
				{
					output1+='\
						<tr>\
							<td>'+data[0].prod_order_status[i].order_status+'</td>\
							<td>';
							for(var j=0;j<data[0].prod_order_status[i].status_details.length;j++)
							{
								output1+='<p>'+data[0].prod_order_status[i].status_details[j].date+' => '+data[0].prod_order_status[i].status_details[j].prd_ids+'</p>';
							}
							output1+='</td>\
						</tr>\
					';
				}
				output1+='\
						</table>\
					</div>\
				';
			}
			$('.order_status_details').html(output1);
		}
	})
	.fail(function(jqXHR, textStatus, error)
	{
		// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$('#modal-loader').hide();
	});
}

function getFranchiseBankDetails(bank_details)
{
	$('.franchise_bank_details').html('');

	var output='\
		<div class="row mb-10">\
			<div class="col-md-12">\
				<h4 class="modal-title">Bank Details</h4>\
			</div>\
		</div>';

	if(bank_details.length > 0)
	{
		output+='\
		<div class="table-responsive">\
			<table class="table table-bordered table-striped table-actions">\
				<tr>\
					<th>Sr. No.</th>\
					<th>Bank Name</th>\
					<th>Account Holder</th>\
					<th>Account No.</th>\
					<th>IFSC</th>\
					<th>Branch</th>\
					<th>Date</th>\
				</tr>';

		for(var i=0;i<bank_details.length;i++)
		{
			output+='\
				<tr>\
					<td>'+bank_details[i].sr_no+'</td>\
					<td>'+bank_details[i].bank_name+'</td>\
					<td>'+bank_details[i].account_holder_name+'</td>\
					<td>'+bank_details[i].account_number+'</td>\
					<td>'+bank_details[i].ifsc_code+'</td>\
					<td>'+bank_details[i].branch_name+'</td>\
					<td>'+bank_details[i].date+'</td>\
				</tr>';
		}

		output+='\
			</table>\
		</div>';
	}
	
	$('.franchise_bank_details').html(output);
}

function getFranchiseDocuments(documents)
{
	$('.franchise_doc_details').html('');

	var output='\
		<div class="row mb-10">\
			<div class="col-md-12">\
				<h4 class="modal-title">Documents</h4>\
			</div>\
		</div>';

	if(documents.length > 0)
	{
		output+='\
		<div class="table-responsive">\
			<table class="table table-bordered table-striped table-actions">\
				<tr>\
					<th>Sr. No.</th>\
					<th>Document Type</th>\
					<th>File</th>\
					<th>Date</th>\
				</tr>';

		for(var i=0;i<documents.length;i++)
		{
			output+='\
				<tr>\
					<td>'+documents[i].sr_no+'</td>\
					<td>'+documents[i].doc_type+'</td>\
					<td><a href="'+documents[i].file_path+'" target="_blank">View</a></td>\
					<td>'+documents[i].date+'</td>\
				</tr>';
		}

		output+='\
			</table>\
		</div>';
	}

	$('.franchise_doc_details').append(output);
}

function roleIcon(role) {
    if (role === 'SMRA') return '👑';
    if (role === 'MRA') return '🏢';
    if (role === 'RA') return '🔗';
    return '👤';
}

function renderNode(node) {
    let html = `
    <div class="hierarchy-node">
        <div class="node-title role-${node.model}" 
             onclick='toggleNode(this, ${JSON.stringify(node)})'>
            <i>${roleIcon(node.model)}</i>
            ${node.name} <small>(${node.model})</small>
        </div>`;

    if (node.children && node.children.length) {
        html += `<div class="node-children">`;
        node.children.forEach(child => {
            html += renderNode(child);
        });
        html += `</div>`;
    }

    html += `</div>`;
    return html;
}

function toggleNode(el, node) {
    const parent = el.parentElement;
    parent.classList.toggle('open');
    showDetails(node);
}

function showDetails(node) {
    document.getElementById("detailPanel").innerHTML = `
        <h4>${node.name}</h4>
        <p><strong>Role:</strong> ${node.model}</p>
        <p><strong>Mobile:</strong> ${node.mobile || '-'}</p>
        <p><strong>Email:</strong> ${node.email || '-'}</p>
        <p><strong>Status:</strong> ${node.status || '-'}</p>
    `;
}

function resetHierarchy()
{
	$(".hierarchy-container").html('\
		<div class="hierarchy-wrapper" id="hierarchyTree"></div>\
        <div class="hierarchy-detail" id="detailPanel">\
			<h4>Franchise Details</h4>\
			<div class="detail-body">\
				<p>Select a franchise to view details</p>\
			</div>\
		</div>');
}

function getTradingBankDetails(bank_details)
{
	$('.trading_bank_details').html('');

	var output='\
		<div class="row mb-10">\
			<div class="col-md-12">\
				<h4 class="modal-title">Bank Details</h4>\
			</div>\
		</div>';

	if(bank_details.length > 0)
	{
		output+='\
		<div class="table-responsive">\
			<table class="table table-bordered table-striped table-actions">\
				<tr>\
					<th>Sr. No.</th>\
					<th>Bank Name</th>\
					<th>Account Holder</th>\
					<th>Account No.</th>\
					<th>IFSC</th>\
					<th>Branch</th>\
					<th>Date</th>\
				</tr>';

		for(var i=0;i<bank_details.length;i++)
		{
			output+='\
				<tr>\
					<td>'+bank_details[i].sr_no+'</td>\
					<td>'+bank_details[i].bank_name+'</td>\
					<td>'+bank_details[i].account_holder_name+'</td>\
					<td>'+bank_details[i].account_number+'</td>\
					<td>'+bank_details[i].ifsc_code+'</td>\
					<td>'+bank_details[i].branch_name+'</td>\
					<td>'+bank_details[i].date+'</td>\
				</tr>';
		}

		output+='\
			</table>\
		</div>';
	}
	else
	{
		output+='\
		<div class="table-responsive">\
			<table class="table table-bordered table-striped table-actions">\
				<tr>\
					<th>No Data Found</th>\
				</tr>\
			</table>\
		</div>';
	}
	$('.trading_bank_details').html(output);
}

function getTradingDocuments(documents)
{
	$('.trading_doc_details').html('');

	var output='\
		<div class="row mb-10">\
			<div class="col-md-12">\
				<h4 class="modal-title">Documents</h4>\
			</div>\
		</div>';

	if(documents.length > 0)
	{
		output+='\
		<div class="table-responsive">\
			<table class="table table-bordered table-striped table-actions">\
				<tr>\
					<th>Sr. No.</th>\
					<th>Document Type</th>\
					<th>File</th>\
					<th>Date</th>\
				</tr>';

		for(var i=0;i<documents.length;i++)
		{
			output+='\
				<tr>\
					<td>'+documents[i].sr_no+'</td>\
					<td>'+documents[i].doc_type+'</td>\
					<td><a href="'+documents[i].file_path+'" target="_blank">View</a></td>\
					<td>'+documents[i].date+'</td>\
				</tr>';
		}

		output+='\
			</table>\
		</div>';
	}
	else
	{
		output+='\
		<div class="table-responsive">\
			<table class="table table-bordered table-striped table-actions">\
				<tr>\
					<th>No Data Found</th>\
				</tr>\
			</table>\
		</div>';
	}
	$('.trading_doc_details').append(output);
}