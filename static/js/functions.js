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

    /*
    Spec buttons
    */
    $(".select-input").click(function () {
        SelectInputButton(this)
    });

    $(".select-module").click(function () {
        console.log("clicked")
        SelectModuleButton(this)
    });
});

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
    var selectedHTML = `<h1 class='p-4 h1-input-selected input-value'>` +  moduleName + `</h1>`

    /* Make the list invisible */
    $(".input-dropdown").toggle()
    /* Modify the card appearance to show it's selected */
    $(".input-card").html(selectedHTML)
    $(".input-card").addClass("card-input-filled")
}

function SelectModuleButton(obj) {
    var moduleName = $(obj).attr('data-name');

    /* Use the name, which'll be used by teh spec, as well as display it. */
    var selectedHTML = `<div class="card-input-filled card text-center module-card"><h1 class='p-4 h1-input-selected input-value'>` +  moduleName + `</h1></div>`
    $(".selected-module-container").html(selectedHTML)

}