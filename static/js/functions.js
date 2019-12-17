const API_ADD = "/api/config"


$(document).ready(function () {
    $(".save").click(function () {
        ClickAddButton(this)
    });

    $(".edit").click(function () {
        ClickEditButton(this)
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

    fetch(API_ADD + "/" + moduleType, {
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
    var moduleType = 'input';
    var moduleName = $(obj).attr('data-name');

    var formId = $(obj).attr('data-target');
    var url = API_ADD + "/" + moduleType + "/" + moduleName;
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