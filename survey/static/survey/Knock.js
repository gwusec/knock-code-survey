// Written by Genry Krichevsky --- edited by Adam J. Aviv and Philipp Markert
// genry@svegasoft.com

//stores enteredCode
Lockr.prefix = prefix;
var knock_code = Lockr.get("knock_code", []);
var cur_code = "";
var attempts = Lockr.get("attempts", []); //for recalling
var taps = Lockr.get("taps", []);

//updates current code
function knock(quad, scenario, next_text, dynamic_instruction, treatment){
    if(cur_code.length < 10) {
        add_value_to_lockr("taps", quad);
        cur_code += quad; //save number
        Lockr.set("cur_code", cur_code);
        addKnockImage(quad, treatment);
        checkInput(scenario, next_text, dynamic_instruction);
    }
    if(cur_code.length == 10) {
        $('#scenario_text').html("Knock Code must be tapped up to 10 times.");
    }
}

function addKnockImage(quad, treatment){
    var element = $('#knock-code-images');
    suffix = "small"
    if (treatment == "big") {
        suffix = "big";
    }
    switch(quad) {
        case "0":
            imageName = "0-" + suffix + ".png";
            break;
        case "1":
            imageName = "1-" + suffix + ".png";
            break;
        case "2":
            imageName = "2-" + suffix + ".png";
            break;
        case "3":
            imageName = "3-" + suffix + ".png";
            break;
        case "4":
            imageName = "4-" + suffix + ".png";
            break;
        case "5":
            imageName = "5-" + suffix + ".png";
            break;
    }
    var widthAndHeight = (screen.width - 102) / 10;
    new_element = '<img src="static/survey/images/' + imageName + '" class="knock-image" style="width:' + widthAndHeight + 'px; height:' + widthAndHeight + 'px;">';
    element.append(new_element)
}

function checkInput(scenario, next_text, dynamic_instruction){
    $('#continue_practice_btn').css("display", "none");
    $('#cancel_btn').css("display", "none");
    $('#reset_btn').css("display", "inline-block");
    $('#next_btn').css("display", "inline-block");
    practice_text_if_code_not_sufficient = scenario;
    practice_text_if_enough_lengh = "Tap at least 3 different regions.";
    practice_text_if_enough_quads = "Tap the regions of the pad at least 6 times.";
    practice_text_if_code_sufficient = next_text;

    var scenario_text = $('#scenario_text');
    scenario_text.height(scenario_text.height());

    css_code_sufficient = {"background-color": "gray", "border": "none", "color": "white"};
    css_code_insufficient = {"background-color": "#cccccc", "border": "1px solid #999999", "color": "#666666"};

    if (dynamic_instruction == "true") {
        if(cur_code.length > 5 && quadrants(cur_code) > 2){
            scenario_text.html(practice_text_if_code_sufficient);
            $('#next_btn').css(css_code_sufficient);
            $('#next_btn').attr("disabled", false);
        } else if (cur_code.length > 5) {
            scenario_text.html(practice_text_if_enough_lengh);
            $('#next_btn').css(css_code_insufficient);
            $('#next_btn').attr("disabled", true);
        } else if (quadrants(cur_code) > 2) {
            scenario_text.html(practice_text_if_enough_quads);
            $('#next_btn').css(css_code_insufficient);
            $('#next_btn').attr("disabled", true);
        } else {
            scenario_text.html(practice_text_if_code_not_sufficient);
            $('#next_btn').css(css_code_insufficient);
            $('#next_btn').attr("disabled", true);
        }
    } else {
        if(cur_code.length > 5) {
            $('#next_btn').css(css_code_sufficient);
            $('#next_btn').attr("disabled", false);
        } else {
            $('#next_btn').css(css_code_insufficient);
            $('#next_btn').attr("disabled", true);
            scenario_text.html(practice_text_if_code_not_sufficient);
        }
    }
}

//returns number of quadrants used
function quadrants(code){
    var quads = [0,0,0,0,0,0];
    for(i in code){
        if(quads[code[i]] == 0)
            quads[code[i]] = 1;
    }
    var tot=0;
    for(i in quads)
        tot += quads[i];
    return tot;
}

function reset(scenario){
    add_value_to_lockr("taps", "reset");
    $('#knock-code-images').empty();
    knock_code.push(cur_code);
    Lockr.set("knock_code", knock_code);
    cur_code = "";
    Lockr.set("cur_code", cur_code);
    checkInput(scenario);
}

function confirmReset(scenario){
    reset(scenario);
    $('#cancel_btn').css("display", "inline-block");
    $('#reset_btn').css("display", "none");
}

function add_value_to_lockr(key, value) {
    var lockr = Lockr.get(key, []);
    lockr.push(value);
    Lockr.set(key, lockr);
}

//-------------------------------------------------
//Practice Workflow

function pract_next(){
    add_value_to_lockr("taps", "next");
    if(cur_code.length > 5 && quadrants(cur_code) > 2){
        $('#scenario_text').html("Knock Code succesfully entered. <br>Keep practicing or click Continue to proceed in the study.");
        //save the code, reset cur
        knock_code.push(cur_code);
        Lockr.set("knock_code", knock_code);
        cur_code = "";
        Lockr.set("cur_code", cur_code);
        $('#knock-code-images').empty();
        $('#next_btn').css("display", "none");
        $('#continue_practice_btn').css("display", "inline-block");
    }
}

function pract_continue(){
    add_value_to_lockr("taps", "continue");
    document.getElementById("code").value = JSON.stringify(knock_code); //keep it as a list
    Lockr.set("endtime", Date.now());
    document.getElementById("time").value = JSON.stringify({starttime: Lockr.get("starttime"), 
                                                            endtime: Lockr.get("endtime"), 
                                                            elapsedtime: Lockr.get("endtime") - Lockr.get("starttime")});
    document.getElementById("taps").value = JSON.stringify(Lockr.get("taps"));
    form = document.getElementById("resultForm");
    Lockr.flush();
    form.submit();
}


//---------------------------------------------------------
//Entry Workflow
function entry_next(){
    add_value_to_lockr("taps", "next");
    if(cur_code.length > 5 && quadrants(cur_code) > 2){
        knock_code.push(cur_code);
        Lockr.set("knock_code", knock_code);
        if (blacklist.indexOf(cur_code) == -1) {
            cur_code = "";
            Lockr.set("cur_code", cur_code);
            document.getElementById("code").value = JSON.stringify(knock_code); //keep it as a list
            Lockr.set("endtime", Date.now());
            document.getElementById("time").value = JSON.stringify({starttime: Lockr.get("starttime"), 
                                                                    endtime: Lockr.get("endtime"), 
                                                                    elapsedtime: Lockr.get("endtime") - Lockr.get("starttime")});
            document.getElementById("taps").value = JSON.stringify(Lockr.get("taps"));
            document.getElementById("hitblacklist").value = Lockr.get("hitblacklist", false);
            form = document.getElementById("resultForm");
            form.submit();
        } else {
            add_value_to_lockr("taps", "hitblacklist");
            Lockr.set("hitblacklist", true);
            $('#blacklistModal').modal({ keyboard: false, backdrop: 'static' });
        }
    }
}

//---------------------------------------------------------
//Confirm Workflow

function confirm_confirm(code, scenario) {
    add_value_to_lockr("taps", "confirm");
    if(cur_code == code){
        $('#knock-code-images').html("");
        $('#scenario_text').html("Knock Code succesfully confirmed. <br>Click Continue to proceed in the study.");
        $('#reset_btn').css("display", "none");
        $('#cancel_btn').css("display", "none");
        $('#next_btn').css("display", "none");
        $('#continue_confirm_btn').css("display", "inline-block");
        $("[class='square']").css("display", "none");
    } else {
        $('#knock-code-images').empty();
        $('#scenario_text').html("Knock Codes do not match. <br>Please try again or click Cancel to set a new code.");
        $('#reset_btn').css("display", "none");
        $('#cancel_btn').css("display", "inline-block");
        $('#next_btn').css("display", "inline-block");
        $('#continue_confirm_btn').css("display", "none");
        $('#next_btn').css({"background-color": "#cccccc", "border": "1px solid #999999", "color": "#666666"});
    }
    knock_code.push(cur_code);
    Lockr.set("knock_code", knock_code);
    cur_code = "";
    Lockr.set("cur_code", cur_code);
}

function confirm_continue() {
    add_value_to_lockr("taps", "continue");
    document.getElementById("code").value = JSON.stringify(knock_code); //keep it as a list
    Lockr.set("endtime", Date.now());
    document.getElementById("time").value = JSON.stringify({starttime: Lockr.get("starttime"), 
                                                            endtime: Lockr.get("endtime"), 
                                                            elapsedtime: Lockr.get("endtime") - Lockr.get("starttime")});
    document.getElementById("confirmed").value = 1; 
    document.getElementById("taps").value = JSON.stringify(Lockr.get("taps"));
    form = document.getElementById("resultForm");
    Lockr.flush();
    form.submit();
}

function confirm_cancel() {
    add_value_to_lockr("taps", "cancel");
    document.getElementById("code").value = JSON.stringify(knock_code); //keep it as a list
    document.getElementById("confirmed").value = 0; 
    document.getElementById("taps").value = JSON.stringify(Lockr.get("taps"));
    form = document.getElementById("resultForm");
    form.submit();
}

function confirm_check_confirmation(code) {
    if (knock_code.includes(code)) {
        $('#knock-code-images').html("");
        $('#scenario_text').html("Knock Code succesfully confirmed. <br>Click Continue to proceed in the study.");
        $('#reset_btn').css("display", "none");
        $('#cancel_btn').css("display", "none");
        $('#next_btn').css("display", "none");
        $('#continue_confirm_btn').css("display", "inline-block");
        $("[class='square']").css("display", "none");
    }
}

//---------------------------------------------------------
//Recall Workflow

function recall_ok(code, scenario) {
    add_value_to_lockr("taps", "ok");
    attempts.push(cur_code);
    Lockr.set("attempts", attempts);
    if(cur_code == code){
        Lockr.set("recalled", "true");
        $('#scenario_text').html("Knock Code succesfully recalled. <br>Click Continue to proceed in the study.");
        $('#reset_btn').css("display", "none");
        $('#next_btn').css("display", "none");
        $('#cancel_recall_btn').css("display", "none");
        $('#continue_recall_btn').css("display", "inline-block");
        $("[class='square']").css("display", "none");
    } else if (attempts.length >= 3) {
        $('#knock-code-images').empty();
        $('#scenario_text').html("Maximum number of attempts exceeded. <br>Please click Continue to proceed in the study.");
        $('#reset_btn').css("display", "none");
        $('#next_btn').css("display", "none");
        $('#cancel_recall_btn').css("display", "inline-block");
        $('#continue_recall_btn').css("display", "none");
        $("[class='square']").css("display", "none");
    } else {
        $('#knock-code-images').empty();
        $('#scenario_text').html("Knock Codes do not match. <br>Please try again.");
        $('#reset_btn').css("display", "inline-block");
        $('#next_btn').css("display", "inline-block");
        $('#next_btn').css({"background-color": "#cccccc", "border": "1px solid #999999", "color": "#666666"});
        $('#cancel_recall_btn').css("display", "none");
        $('#continue_recall_btn').css("display", "none");
    }
    cur_code = "";
    Lockr.set("cur_code", cur_code);
}

function recall_check_attempts() {
    attempts = Lockr.get("attempts", []);
    if (Lockr.get("recalled", "false") == "true") {
        $('#scenario_text').html("Knock Code succesfully recalled. <br>Click Continue to proceed in the study.");
        $('#reset_btn').css("display", "none");
        $('#next_btn').css("display", "none");
        $('#cancel_recall_btn').css("display", "none");
        $('#continue_recall_btn').css("display", "inline-block");
        $("[class='square']").css("display", "none");
    } else if (attempts.length >= 3) {
        $('#knock-code-images').empty();
        $('#scenario_text').html("Maximum number of attempts exceeded. <br>Please click Continue to proceed in the study.");
        $('#reset_btn').css("display", "none");
        $('#next_btn').css("display", "none");
        $('#cancel_recall_btn').css("display", "inline-block");
        $('#continue_recall_btn').css("display", "none");
        $("[class='square']").css("display", "none");
    }
    cur_code = "";
    Lockr.set("cur_code", cur_code);
}

function recall_continue(code_forgotten) {
    if (code_forgotten == "True") {
        add_value_to_lockr("taps", "continue_forgotten");
    } else {        
        add_value_to_lockr("taps", "continue_recalled");
    }
    cur_code = "";
    Lockr.set("cur_code", cur_code);
    Lockr.set("endtime", Date.now());
    document.getElementById("time").value = JSON.stringify({starttime: Lockr.get("starttime"), 
                                                            endtime: Lockr.get("endtime"), 
                                                            elapsedtime: Lockr.get("endtime") - Lockr.get("starttime")});
    document.getElementById("attempts").value = JSON.stringify(attempts); //keep it as a list
    document.getElementById("forgot").value = code_forgotten; 
    document.getElementById("taps").value = JSON.stringify(Lockr.get("taps"));
    form = document.getElementById("resultForm");
    Lockr.flush();
    form.submit();
}