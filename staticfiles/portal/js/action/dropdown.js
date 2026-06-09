function fill_metal(metal_id="")
{
	$.ajax({
		url: window.APP_URLS.metal_list,
		type: 'GET',
	})
	.done(function(response)
	{
		// console.log(response)
		$(".metal").html("<option value=''>Choose Metal</option>");
		for ( i = 0; i < response.length; i++ ) 
		{
			if (metal_id!="" && metal_id==response[i].metal_id)
			{
				$(".metal").append("<option value='"+response[i].metal_id+"' selected>"+response[i].metal_name+"</option>");
			}
			else
			{
				$(".metal").append("<option value='"+response[i].metal_id+"'>"+response[i].metal_name+"</option>");
			}
		}
	})
	.fail(function(jqXHR, textStatus, error)
	{
		// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$(".metal").parent().find("span").remove();
		$(".metal").parent().closest('div').append('<span class="error">Error loading metal!</span>')
	});
}

$(document).on('change', '.metal', function(e)
{
	var id = $(this).attr('id');
	var purity_id = "";
	if(id=="metal")
	{
		purity_id = "purity";
	} 
	else if(id=="metal_e")
	{
		purity_id = "purity_e";
	} 
	var metal_id=$(this).val();
	// console.log("Metal Id :: "+metal_id);
	if(metal_id!="")
	{
		fill_purity(metal_id,purity_id);
		fill_type(metal_id)
	}
	else
	{
		$('#'+purity_id).val('');
		$('#'+purity_id).trigger('change');
		$('#metal_type').val('');
		$('#metal_type').trigger('change');
	}
});

function fill_purity(metal_id="",purity_id="",purityUid="")
{
	// alert(metal_id)
	// alert(purity_id)
	$.ajax({
		url: window.APP_URLS.purity_list,
		type: 'GET',
		data:{
			metal_id:metal_id
		}
	})
	.done(function(response)
	{
		// console.log(response)
		selected_id=purityUid;
		if(purity_id=="purity_e")
		{
			selected_id=$("#purity_id").val();
		}
		// alert(selected_id)
		$("#"+purity_id).html("<option value=''>Choose Purity</option>");
		for ( i = 0; i < response.length; i++ ) 
		{
			if(selected_id !="" && response[i].purity_id==selected_id)
			{
				$("#"+purity_id).append("<option value='"+response[i].purity_id+"' selected>"+response[i].purity_name+"</option>");
			}
			else
			{
				$("#"+purity_id).append("<option value='"+response[i].purity_id+"'>"+response[i].purity_name+"</option>");
			}
		}
	})
	.fail(function(jqXHR, textStatus, error)
	{
		// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$("#"+purity_id).parent().find("span").remove();
		$("#"+purity_id).parent().closest('div').append('<span class="error">Error loading purity!</span>')
	});
}

function fill_type(metal_id="",typeUid="")
{
	$.ajax({
		url: window.APP_URLS.type_list,
		type: 'GET',
		data:{
			metal_id:metal_id
		}
	})
	.done(function(response)
	{
		// console.log(response)
		selected_id="";
		if(typeUid!="")
		{
			selected_id=typeUid;
		}
		$("#metal_type").html("<option value=''>Choose Type</option>");
		for ( i = 0; i < response.length; i++ ) 
		{
			if(selected_id !="" && response[i].type_id==selected_id)
			{
				$("#metal_type").append("<option value='"+response[i].type_id+"' selected>"+response[i].type_name+"</option>");
			}
			else
			{
				$("#metal_type").append("<option value='"+response[i].type_id+"'>"+response[i].type_name+"</option>");
			}
		}
	})
	.fail(function(jqXHR, textStatus, error)
	{
		// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$("#metal_type").parent().find("span").remove();
		$("#metal_type").parent().closest('div').append('<span class="error">Error loading type!</span>')
	});
}

function fill_category(category_id="")
{
	// alert(category_id)
	$.ajax({
		url: window.APP_URLS.getAllCategory,
		type: 'GET',
	})
	.done(function(response)
	{
		// console.log(response)
		$("#category").html("<option value=''>Choose Category</option>");
		for ( i = 0; i < response.length; i++ ) 
		{
			if (category_id!="" && category_id==response[i].category_id)
			{
				$("#category").append("<option value='"+response[i].category_id+"' selected>"+response[i].category_name+"</option>");
			}
			else
			{
				$("#category").append("<option value='"+response[i].category_id+"'>"+response[i].category_name+"</option>");
			}
		}
	})
	.fail(function(jqXHR, textStatus, error)
	{
		// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$("#category").parent().find("span").remove();
		$("#category").parent().closest('div').append('<span class="error">Error loading category!</span>')
	});
}

function fill_gender_category()
{
	$.ajax({
		url: window.APP_URLS.getAllGenders,
		type: 'GET',
	})
	.done(function(response)
	{
		// console.log(response)
		$("#gender_category").html("");
		var op = "";
		for ( i = 0; i < response.length; i++ ) 
		{
			op += '\
				<div class="col-md-12">\
					<input type="checkbox" class="filled-in chk-col-primary" id="gen_'+response[i].gender_id+'" name="access" value="'+response[i].gender_id+'"/>\
                    <label for="gen_'+response[i].gender_id+'" style="margin-top: 7px;margin-bottom:0px;">'+response[i].gender_name+'</label>\
				</div>';
		}
		$("#gender_category").html(op);
	})
	.fail(function(jqXHR, textStatus, error)
	{
		// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$("#gender_category").append('<span class="error">Error loading category!</span>')
	});
}

function fill_product()
{
	$.ajax({
		url: window.APP_URLS.getAllProduct,
		type: 'GET',
	})
	.done(function(response)
	{
		// console.log(response)
		$("#product").html("<option value=''>Choose Product</option>");
		for ( i = 0; i < response.length; i++ ) 
		{
			$("#product").append("<option value='"+response[i].product_id+"'>"+response[i].product_name+"</option>");
		}
	})
	.fail(function(jqXHR, textStatus, error)
	{
		// console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$("#product").parent().find("span").remove();
		$("#product").parent().closest('div').append('<span class="error">Error loading product!</span>')
	});
}

function fill_referral_agent()
{
	$.ajax({
		url: window.APP_URLS.getAllAgents,
		type: 'GET',
	})
	.done(function(response)
	{
		console.log(response)
		$("#referral_agent").html("<option value=''>Choose Agent</option>");
		for ( i = 0; i < response.length; i++ ) 
		{
			$("#referral_agent").append("<option value='"+response[i].referral_id+"'>"+response[i].holder_name+"("+response[i].referral_id+")</option>");
		}
	})
	.fail(function(jqXHR, textStatus, error)
	{
		console.log(jqXHR.responseText+" | "+textStatus+" | "+error)
		$("#referral_agent").parent().find("span").remove();
		$("#referral_agent").parent().closest('div').append('<span class="error">Error loading agent!</span>')
	});
}