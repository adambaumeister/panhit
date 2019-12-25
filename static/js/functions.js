const API_ROUTE = "/api/config"


$(document).ready(function () {
    /*
    Config buttons
    */
    $(".save").click(function () {
        ClickAddButton(this)
    });

    $(".edit").click(function () {
        ClickEditButton(this)
    });

    $(".delete").click(function () {
        ClickDeleteButton(this)
    });

    $(".add-list-item").click(function () {
        ClickListAddButton(this)
    });

    /*
    Spec buttons
    */
    $(".select-input").click(function () {
        SelectInputButton(this)
        ScanSpecSettings();
    });

    $(".select-module").click(function () {
        SelectModuleButton(this);
        ScanSpecSettings();
    });
});

function ClickListAddButton(obj) {
    /* Clicking the little + button next to a list type input */
    var targetList = "#" + $(obj).attr('data-target');
    
    inputs = [];
    // Get the count of current input fields
    $(targetList + " :input").each(function () {
        inputs.push(this);
    })
    inputHtml = '<input class="form-control" name="' + $(inputs[0]).attr('name') + "-" + inputs.length + '">'
    $(targetList).append(inputHtml)

}

function ClickAddButton(obj) {
    var moduleType = $(obj).attr('data-type');
    var moduleName = $(obj).attr('data-module');
    var formId = "#" + moduleName + "-form";

    var data = {}
    $(formId + " :input").each(function () {
        data[$(this).attr('name')] = $(this).val()
    })
    data['type'] = moduleName;

    fetch(API_ROUTE + "/" + moduleType, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);

                $(obj).text("Failed!");
                $(obj).addClass("btn-success").removeClass("btn-primary")
                return;
            }

            // Examine the text in the response
            response.json().then(function (data) {
                // If the operation is gucci gang gucci gang gucci gang
                if (data['status'] === 0) {
                    $(obj).text("Added!");
                    $(obj).addClass("btn-danger").removeClass("btn-primary")

                    location.reload()
                }
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function ClickEditButton(obj) {
    var moduleType = $(obj).attr('data-type');
    var moduleName = $(obj).attr('data-name');

    var formId = $(obj).attr('data-target');
    var url = API_ROUTE + "/" + moduleType + "/" + moduleName;
    console.log(url)
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);

                $(obj).text("Failed!");
                $(obj).addClass("btn-success").removeClass("btn-primary")
                return;
            }

            response.json().then(function (data) {
                var moduleClass = data['items'][0]['type']
                $.each(data['items'][0], function(k, v) {
                    var selector = "#"+moduleClass+"-"+k+"-input"
                    console.log(selector)
                    $("#"+moduleClass+"-"+k+"-input").val(v)
                }); 
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}

function ClickDeleteButton(obj) {
    var moduleType = $(obj).attr('data-type');
    var moduleName = $(obj).attr('data-name');

    var url = API_ROUTE + "/" + moduleType + "/" + moduleName;
    fetch(url, {
        method: 'DELETE',
    }).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);

                $(obj).text("Failed!");
                $(obj).addClass("btn-success").removeClass("btn-primary")
                return;
            }

            response.json().then(function (data) {
                if (data['status'] === 0) {
                    $(obj).text("Deleted!");
                    $(obj).addClass("btn-danger").removeClass("btn-primary")

                    location.reload()
                }
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}

function SelectInputButton(obj) {
    var moduleName = $(obj).attr('data-name');

    /* Use the name, which'll be used by teh spec, as well as display it. */
    var selectedHTML = `<h2 class='p-3 h1-input-selected input-value'>` +  moduleName + `</h1>`

    /* Make the list invisible */
    $(".input-dropdown").toggle()
    /* Modify the card appearance to show it's selected */
    $(".input-card").html(selectedHTML)
    $(".input-card").addClass("card-input-filled")
}

function SelectModuleButton(obj) {
    var moduleName = $(obj).attr('data-name');

    $(".module-dropdown").text("Pick another module...")
    /* Use the name, which'll be used by teh spec, as well as display it. */
    var selectedHTML = `<div class="card-module-filled card text-center module-card mb-3"><h2 class='p-3 h1-module-selected module-value'>` +  moduleName + `</h2></div>`
    $(".selected-module-container").append(selectedHTML)

}

function ScanSpecSettings () {
    /* Scans the spec page to ensure the user as selected an input, at least one module, and an output */
    var items = $(".selected-module-container").find("h2"); 
    var inputName = $(".input-value").text(); 


    var data = {
        'spec': {
            'inputs': [inputName],
            'modules': []
        }
    }; 

    items.each(function () {
        data['spec']['modules'].push($(this).text())
    })

    if (data['spec']['modules'].length > 0) {
        $(".run").removeClass("d-none")
    }
}