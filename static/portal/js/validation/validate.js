$(document).ready(function(){
    (function($) {
        "use strict";
		$("#btn_addMetalPurityPrice").click(function(e) 
		{
			$('#frm_addMetalPurityPrice').validate({
				rules:
				{
					metal: 
					{
						required: true
					},
					purity: 
					{
						required: true
					},
					price:
					{
						required: true
					}
				},
				messages:
				{
					metal: 
					{
						required: "Please choose metal"
					},
					purity: 
					{
						required: "Please choose purity"
					},
					price:
					{
						required:"Please enter price"
					}
				},
				submitHandler: function(form) 
				{
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.addPurityPrice,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_addMetalPurityPrice").validate();
									validator.resetForm();
									fill_metal();
									$('#purity').val('');
									$('#purity').trigger('change');
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
								// console.log(error);
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
					})
				}
			})
		})
		$("#btn_editMetalPurityPrice").click(function(e) {
			$('#frm_editMetalPurityPrice').validate({
				rules:
				{
					metal: 
					{
						required: true
					},
					purity: 
					{
						required: true
					},
					price:
					{
						required: true
					}
				},
				messages:
				{
					metal: 
					{
						required: "Please choose metal"
					},
					purity: 
					{
						required: "Please choose purity"
					},
					price:
					{
						required:"Please enter price"
					}
				},
				submitHandler: function(form) {
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.updatePurityPrice,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_editMetalPurityPrice").validate();
									validator.resetForm();
									$('#edit-modal').modal('hide');

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
						error: function(jqXHR, textStatus, error) 
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
					})
				}
			})
		})
		$("#btn_addUnit").click(function(e) 
		{
			$('#frm_addUnit').validate({
				rules:
				{
					unit: 
					{
						required: true
					}
				},
				messages:
				{
					unit:
					{
						required:"Please enter unit"
					}
				},
				submitHandler: function(form) 
				{
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.addUnit,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_addUnit").validate();
									validator.resetForm();
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
								// console.log(error);
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
					})
				}
			})
		})
		$("#btn_editUnit").click(function(e) {
			$('#frm_editUnit').validate({
				rules:
				{
					unit: 
					{
						required: true
					}
				},
				messages:
				{
					unit:
					{
						required:"Please enter unit"
					}
				},
				submitHandler: function(form) {
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.updateUnit,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_editUnit").validate();
									validator.resetForm();
									$('#edit-modal').modal('hide');

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
						error: function(jqXHR, textStatus, error) 
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
					})
				}
			})
		})
		$("#btn_addCategory").click(function(e) 
		{
			$('#frm_addCategory').validate({
				rules:
				{
					name: 
					{
						required: true
					}
				},
				messages:
				{
					name:
					{
						required:"Please enter name"
					}
				},
				submitHandler: function(form) 
				{
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.addCategory,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_addCategory").validate();
									validator.resetForm();
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
								// console.log(error);
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
					})
				}
			})
		})
		$("#btn_editCategory").click(function(e) {
			$('#frm_editCategory').validate({
				rules:
				{
					name: 
					{
						required: true
					}
				},
				messages:
				{
					name:
					{
						required:"Please enter name"
					}
				},
				submitHandler: function(form) {
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.updateCategory,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_editCategory").validate();
									validator.resetForm();
									$('#edit-modal').modal('hide');

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
						error: function(jqXHR, textStatus, error) 
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
					})
				}
			})
		})
		$("#btn_addProduct").click(function(e) 
		{
			$('#frm_addProduct').validate({
				rules:
				{
					name: 
					{
						required: true
					},
					category: 
					{
						required: true
					},
					size:
					{
						required: true
					},
					metal: 
					{
						required: true
					},
					metal_type: 
					{
						required: true
					},
					purity: 
					{
						required: true
					},
					weight: 
					{
						required: true
					},
					gst: 
					{
						required: true
					},
				},
				messages:
				{
					name: 
					{
						required: "Product name is mandatory"
					},
					category: 
					{
						required: "Category is mandatory"
					},
					size:
					{
						required: "Product size is mandatory"
					},
					metal: 
					{
						required: "Metal is mandatory"
					},
					metal_type: 
					{
						required: "Metal type is mandatory"
					},
					purity: 
					{
						required: "Purity is mandatory"
					},
					weight: 
					{
						required: "Weight is mandatory"
					},
					gst: 
					{
						required: "Gst is mandatory"
					},
				},
				submitHandler: function(form) 
				{
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.addProduct,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_addProduct").validate();
									validator.resetForm();
									fill_category();
									fill_metal();
									$('#purity').val('');
									$('#purity').trigger('change');
									$('#metal_type').val('');
									$('#metal_type').trigger('change');
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
								// console.log(error);
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
					})
				}
			})
		})
		$("#btn_updateProduct").click(function(e) 
		{
			$('#frm_updateProduct').validate({
				rules:
				{
					name: 
					{
						required: true
					},
					category: 
					{
						required: true
					},
					size:
					{
						required: true
					},
					metal: 
					{
						required: true
					},
					metal_type: 
					{
						required: true
					},
					purity: 
					{
						required: true
					},
					weight: 
					{
						required: true
					},
					gst: 
					{
						required: true
					},
				},
				messages:
				{
					name: 
					{
						required: "Product name is mandatory"
					},
					category: 
					{
						required: "Category is mandatory"
					},
					size:
					{
						required: "Product size is mandatory"
					},
					metal: 
					{
						required: "Metal is mandatory"
					},
					metal_type: 
					{
						required: "Metal type is mandatory"
					},
					purity: 
					{
						required: "Purity is mandatory"
					},
					weight: 
					{
						required: "Weight is mandatory"
					},
					gst: 
					{
						required: "Gst is mandatory"
					},
				},
				submitHandler: function(form) 
				{
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.updateProduct,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
								// console.log(error);
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
					})
				}
			})
		})
		$("#btn_addImageSlider").click(function(e) 
		{
			$('#frm_addImageSlider').validate({
				rules:
				{
					image_type: 
					{
						required: true
					},
					sequence: 
					{
						required: true,
						digits:true
					},
					image:
					{
						required: true
					}
				},
				messages:
				{
					image_type: 
					{
						required: "Please choose image type"
					},
					sequence:
					{
						required:"Please enter sequence",
						digits:"Only numbers allowed"
					},
					image:
					{
						required:"Image upload is mandatory"
					}
				},
				submitHandler: function(form) 
				{
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.addImage,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_addImageSlider").validate();
									validator.resetForm();

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
					})
				}
			})
		})
		$("#btn_changeStatus").click(function(e) {
			$('#frm_changeStatus').validate({
				rules:
				{
					date: 
					{
						required: true
					},
					order_status: 
					{
						required: true
					}
				},
				messages:
				{
					date: 
					{
						required: "Please choose date and time"
					},
					order_status: 
					{
						required: "Please choose order status"
					}
				},
				submitHandler: function(form) {
					Swal.fire({
						title: "Are you sure?",
						text: "You want to update the status.",
						icon: 'warning',
						showCancelButton: true,
						confirmButtonColor: '#3085d6',
						cancelButtonColor: '#d33',
						confirmButtonText: 'Yes!'
					}).then((result) => {
						if (result.isConfirmed) 
						{
							$('#frm_changeStatus').ajaxSubmit({
								type:"POST",
								data:{
									btn_changeStatus:'btn_changeStatus',
									order_id:$("#order_id").val(),
									chk_checked_prod_ids:$("#chk_checked_prod_ids").val(),
									date:$("#date").val(),
									order_status:$("#order_status").val(),
									csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
								},
								url:window.APP_URLS.updateOrderStatus,
								dataType : "json",
								success: function(response) 
								{
									// console.log(response);
									try
									{
										if(response.success==1)
										{
											var res="";
											for (var i = 0; i < response.message.length; i++) 
											{
												// console.log(response.message[i]);
												res+='<p class="swal-para text text-'+response.message[i].msg_type+'">'+response.message[i].msg+'</p>';
											}
		
											Swal.fire('',res,'success');
		
											// $.toast({
											// 	heading: 'Success',
											// 	text: response.message,
											// 	position: 'top-right',
											// 	loaderBg: '#ff6849',
											// 	icon: 'success',
											// 	hideAfter: 3500,
											// 	stack: 6
											// });
											var validator = $("#frm_changeStatus").validate();
											validator.resetForm();
											$('#edit-modal').modal('hide');
											$('.modal').css('overflow-y', 'auto');
		
											// load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),$("#access").val(),$('#limit').val());
		
											getCustomerOrderDetails($("#order_id").val());
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
										// console.log(error);
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
							})
						}
					})
				}
			})
		})
		$("#btn_addStock").click(function(e) 
		{
			$('#frm_addStock').validate({
				rules:
				{
					product: 
					{
						required: true
					},
					quantity:
					{
						required: true
					}
				},
				messages:
				{
					product: 
					{
						required: "Product is mandatory"
					},
					quantity:
					{
						required: "Quantity is mandatory"
					}
				},
				submitHandler: function(form) 
				{
					$(form).ajaxSubmit({
						type:"POST",
						data: $(form).serialize(),
						url:window.APP_URLS.addStock,
						dataType : "json",
						success: function(response) 
						{
							// console.log(response);
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
									var validator = $("#frm_addStock").validate();
									validator.resetForm();
									fill_product();

									load_data($('ul.pagination').find('li.active>a').data('page_number'),$("#type").val(),$('#search').val(),$("#from_date").val(),$("#to_date").val(),'',$('#limit').val());
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
								// console.log(error);
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
					})
				}
			})
		})
		$("#btn_addUser").click(function (e) {
			$('#frm_addUser').validate({
				rules:
				{
					name:
					{
						required: true
					},
					mobile_number:
					{
						required: true,
						digits: true,
						maxlength: 10,
						minlength: 10
					},
					email:
					{
						required: true,
						email: true
					},
					// role:
					// {
					// 	required: true
					// }
				},
				messages:
				{
					name:
					{
						required: "Please enter name"
					},
					mobile_number:
					{
						required: "Please enter mobile number",
						digits: "Only numbers allowed",
						maxlength: "Mobile number should not be more than 10 digits",
						minlength: "Mobile number should not be less than 10 digits",
					},
					email:
					{
						required: "Please enter email",
						email: "Please enter valid email id"
					},
					// role:
					// {
					// 	required: "Please select user role"
					// }
				},
				submitHandler: function (form) {
					$(form).ajaxSubmit({
						type: "POST",
						data: $(form).serialize(),
						url: window.APP_URLS.addPortalUser,
						dataType: "json",
						success: function (response) {
							// console.log(response);
							try {
								if (response.success == 1) {
									$.toast({
										heading: 'Success',
										text: response.message,
										position: 'top-right',
										loaderBg: '#ff6849',
										icon: 'success',
										hideAfter: 3500,
										stack: 6
									});
									var validator = $("#frm_addUser").validate();
									validator.resetForm();
									load_data($('ul.pagination').find('li.active>a').data('page_number'), $("#type").val(), $('#search').val(), $("#from_date").val(), $("#to_date").val(), $("#access").val(), $('#limit').val());
								}
								else {
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
							catch (error) {
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
						error: function (jqXHR, textStatus, error) {
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
					})
				}
			})
		})
		$("#btn_editUser").click(function (e) {
			$('#frm_editUser').validate({
				rules:
				{
					name:
					{
						required: true
					},
					mobile_number:
					{
						required: true,
						digits: true,
						maxlength: 10,
						minlength: 10
					},
					email:
					{
						required: true,
						email: true
					},
					// role:
					// {
					// 	required: true
					// }
				},
				messages:
				{
					name:
					{
						required: "Please enter name"
					},
					mobile_number:
					{
						required: "Please enter mobile number",
						digits: "Only numbers allowed",
						maxlength: "Mobile number should not be more than 10 digits",
						minlength: "Mobile number should not be less than 10 digits",
					},
					email:
					{
						required: "Please enter email",
						email: "Please enter valid email id"
					},
					// role:
					// {
					// 	required: "Please select user role"
					// }
				},
				submitHandler: function (form) {
					$(form).ajaxSubmit({
						type: "POST",
						data: $(form).serialize(),
						url: window.APP_URLS.updatePortalUser,
						dataType: "json",
						success: function (response) {
							// console.log(response);
							try {
								if (response.success == 1) {
									$.toast({
										heading: 'Success',
										text: response.message,
										position: 'top-right',
										loaderBg: '#ff6849',
										icon: 'success',
										hideAfter: 3500,
										stack: 6
									});
									var validator = $("#frm_editUser").validate();
									validator.resetForm();
									$('#edit-modal').modal('hide');

									load_data($('ul.pagination').find('li.active>a').data('page_number'), $("#type").val(), $('#search').val(), $("#from_date").val(), $("#to_date").val(), $("#access").val(), $('#limit').val());
								}
								else {
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
							catch (error) {
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
						error: function (jqXHR, textStatus, error) {
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
					})
				}
			})
		})
		$("#btn_transferReferral").click(function (e) {
			$('#frm_transferReferral').validate({
				submitHandler: function (form) {
					$(form).ajaxSubmit({
						type: "POST",
						data: $(form).serialize(),
						url: window.APP_URLS.transferAgent,
						dataType: "json",
						success: function (response) {
							console.log(response);
							try {
								if (response.success == 1) {
									$.toast({
										heading: 'Success',
										text: response.message,
										position: 'top-right',
										loaderBg: '#ff6849',
										icon: 'success',
										hideAfter: 3500,
										stack: 6
									});
									var validator = $("#frm_transferReferral").validate();
									validator.resetForm();
									$('#transfer-modal').modal('hide');

									load_data($('ul.pagination').find('li.active>a').data('page_number'), $("#type").val(), $('#search').val(), $("#from_date").val(), $("#to_date").val(), $("#access").val(), $('#limit').val());
								}
								else {
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
							catch (error) {
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
						error: function (jqXHR, textStatus, error) {
							console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
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
	})(jQuery)
});