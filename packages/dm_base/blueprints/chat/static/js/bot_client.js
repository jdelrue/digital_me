import {default as client} from '/chat/jsclient.js';
var stringContentGenerate = function (message, kwargs){
    return `
    <h4>${message}</h4>
    <div class="form-group">
		<input type="text" class="form-control" id="value">
    </div>`
}

var passwordContentGenerate = function (message, kwargs){
    return `
    <h4>${message}</h4>
    <div class="form-group">
		<input type="password" class="form-control" id="value">
    </div>`
}

var textContentGenerate = function (message, kwargs){
    return `
    <h4>${message}</h4>
    <div class="form-group">
		<textarea rows="4" cols="50" class="form-control" id="value"></textarea>
    </div>`
}

var intContentGenerate = function (message, kwargs){
    return `
    <h4>${message}</h4>
    <div class="form-group">
		<input type="number" class="form-control" id="value">
    </div>`
}

var mdContentGenerate = function (message, kwargs){
    let converter = new showdown.Converter({tables: true, tablesHeaderId: "table"});
    const htmlContents = converter.makeHtml(message);
    return `${htmlContents}`;
}

var multiChoiceGenerate = function(message, options, kwargs){
    let choices = ""
    $.each(options, function(i, value){
        choices += `
        <div class="items col-xs-5 col-sm-5 col-md-3 col-lg-3">
            <div class="info-block block-info clearfix">
                <div data-toggle="buttons" class="btn-group bizmoduleselect">
                    <label class="btn btn-default">
                        <div class="bizcontent">
                            <input type="checkbox" name="value[]" autocomplete="off" value="${value}">
                            <span class="glyphicon glyphicon-ok glyphicon-lg"></span>
                            <h5>${value}</h5>
                        </div>
                    </label>
                </div>
            </div>
        </div>`;
    });
    let contents = `
    <h4>${message}</h4>
    <div class="form-group">
        <div class="checkbox-container">${choices}</div>
    </div>`;
    return contents;
}

var singleChoiceGenerate = function(message, options, kwargs){
    let choices = "";
    const classes = ["primary", "success", "danger", "warning", "info"];
    $.each(options, function(i, value){
        if(i >= classes.length){
            i -= classes.length;
        }
        choices += `
        <div class="funkyradio-${classes[i]}">
            <input type="radio" name="value" id="${value}" value="${value}"/>
            <label for="${value}">${value}</label>
        </div>`;
    });
    let contents = `
    <h4>${message}</h4>
    <div class="funkyradio">${choices}</div>`;
    return contents;
}

var dropDownChoiceGenerate = function(message, options, kwargs){
    let choices = "";
    $.each(options, function(i, value){
        choices += `<option value="${value}">${value}</option>`;
    });
    let contents = `
    <h4>${message}</h4>
    <div class="form-group">
        <select class="form-control" id="value">
            ${choices}
        </select>
    </div>`;
    return contents;
}

var addStep = function(reset){
    if(reset) {
        $(".f1-steps").empty();
    }
    const currentStep = $(".f1-steps").children().length + 1;
	const stepTemplate = `
	<div class="f1-step active">
		<div class="f1-step-icon">${currentStep}</div>
	</div>`;
	$(".f1-step:last-child").removeClass("active");
    $(".f1-steps").append(stepTemplate);
}

var generateSlide = function(res) {
    $("#spinner").toggle();
    // if error: leave the old slide and show the error
    if (res["error"]) {
        $("#error").html(res['error']);
        $(".btn-submit").attr("disabled", "false");
        $(".form-box").toggle({"duration": 400});
        return
    }
    // If the response contains redirect, so this was the final slide and will take new action
    else if(res['cat'] === "redirect"){
            $(location).attr("href", res["msg"]);
            return
    }
    addStep(res['kwargs']['reset']);
    let contents = "";
    switch(res['cat']){
        case "string_ask":
            contents = stringContentGenerate(res['msg'], res['kwargs']);
            break;
        case "password_ask":
            contents = passwordContentGenerate(res['msg'], res['kwargs']);
            break;
        case "text_ask":
            contents = textContentGenerate(res['msg'], res['kwargs']);
            break;
        case "int_ask":
            contents = intContentGenerate(res['msg'], res['kwargs']);
            break;
        case "md_show":
            contents = mdContentGenerate(res['msg'], res['kwargs']);
            break;
        case "multi_choice":
            contents = multiChoiceGenerate(res['msg'], res['options'], res['kwargs'])
            break;
        case "single_choice":
            contents = singleChoiceGenerate(res['msg'], res['options'], res['kwargs'])
            break;
        case "drop_down_choice":
            contents = dropDownChoiceGenerate(res['msg'], res['options'], res['kwargs'])
            break;
    }
	contents = `
        <fieldset>
            <p id="error" class="red"></p>
			${contents}
			<span class="f1-buttons-right">
				<button type="submit" class="btn btn-submit" required="true">Next</button>
			</span>
		</fieldset>`;
    $("#wizard").html(contents);
    $(".form-box").toggle({"duration": 400});

	$(".btn-submit").on("click", function(ev){
        ev.preventDefault();
		let value="";
		if (["string_ask", "int_ask", "text_ask", "password_ask", "drop_down_choice"].includes(res['cat'])) {
			value = $("#value").val();
        } else if (res['cat'] === "single_choice"){
            value = $("input[name='value']:checked").val();
        } else if (res['cat'] === "multi_choice"){
            let values = [];
            $("input[name='value[]']:checked").each( function () {
                values.push($(this).val());
            });
            value = JSON.stringify(values);
        }
        // Validate the input
        const errors = validate(value, res['kwargs']['validate']);
        if (errors.length > 0){
            var ul = $('<ul>');
            $(errors).each(function(index, error) {
                ul.append($('<li>').html(error));
            });
            $("#error").html(ul);
            $("#error").removeClass("hidden");
            return
        }
        $("#error").addClass("hidden");
        $(this).attr("disabled", "disabled");
        $("#spinner").toggle();
        $(".form-box").toggle({"duration": 400});
		client.base_chat.work_report(SESSIONID, value).then(function(res){
		    // Ignore work_report response and wait for getting next question
		    client.base_chat.work_get(SESSIONID).then(function(res){
                res = JSON.parse(res);
                generateSlide(res);
            });
		});
	});
}

client.base_chat.work_get(SESSIONID).then(function(res){
    res = JSON.parse(res);
	generateSlide(res);
});
