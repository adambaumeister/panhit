const API_CONFIG_ROUTE = "/api/config"
const API_ROUTE = "/api"

$(document).ready(function () {
    /*
    Config buttons
    */

    $(".edit").click(function () {
        ClickEditButton(this)
    });

    $(".delete").click(function () {
        ClickDeleteButton(this)
    });

    $(".add-tag").click(function() {
        ClickAddTagButton(this)
    })

    $(".add-item").click(function() {
        ClickAddItemButton(this)
    })

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

    
    $(".run").click(function () {
        ClickRunButton()
    });

    /*
    job page stuff
    */
    // register the next/prev page buttons
    // This works for any table
    var pageNum = $(".page-number").text();
    $(".next-page").click(function () {
        console.log("here")

        pageNum = Number(pageNum) + 1; 
        $(".page-number").text(pageNum);
        // Re-render any visble tables
        ReplaceJobsTable();

    });
    $(".prev-page").click(function () {
        pageNum = Number(pageNum) - 1; 
        $(".page-number").text(pageNum);
        // Re-render any visble tables
        ReplaceJobsTable();
    });

    // Render the jobs table
    ReplaceJobsTable();
    // Render the job result table
    ReplaceResultTable();
});

class ProgressBar {
    // Basic Progress bar, rendered using bootstraps methods.
    constructor(min, max) {
        this.min = min;
        this.max = max;
    }

    render(cur) {
        var txt = '<div class="progress">' +
        '<div class="progress-bar" role="progressbar" style="width:' + cur + '%"  aria-valuenow="'+ cur + '" aria-valuemin="'+ this.min + '" aria-valuemax="'+ this.max + '"></div>' +
        '</div>'
        return txt;
    }
}

function ClickAddTagButton() {

    var url = API_ROUTE + "/config/tags/add";
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.text().then(function (data) {
                console.log(data)
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}

function ClickAddItemButton(obj) {
    var moduleType = $(obj).attr('data-type');
    var moduleName = $(obj).attr('data-module');

    var url = API_CONFIG_ROUTE + "/" + moduleType + "/" + moduleName + "/spec?as_html=true"
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.text().then(function (data) {
                $(".new-config").html(data);
                
                // Register the buttons within the new HTML
                $(".add-list-item").click(function () {
                    ClickListAddButton(this)
                });

                $(".save").click(function () {
                    ClickAddButton(this)
                });
            
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}

function ReplaceResultTable() {
    // get the job id 
    var res = top.location.pathname.split("/");
    var jobID = res[2]

    if (!$('.result').length) {
        return;
    }

    // Set the field we use as the ID,  this gets referenced when the row is clicked
    var idField = 0;
    // Set the field we use as the progress bar, this is an index as returned via the tablular api
    var pbField = 5;

    // Make the API call to get the values
    var pageNum = $(".page-number").text();

    var url = API_ROUTE + "/jobs/" + jobID + "/result?table=true&as_html=true&page="+ pageNum;
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.text().then(function (data) {
                $('.result').html(data);

                var pageNum = $(".page-number").text();
                var pageMax = $(".page-max").text();

                if (Number(pageNum) == Number(pageMax)) {
                    $(".next-page").attr("disabled", true)
                } 

                if (Number(pageNum) == 0) {
                    $(".prev-page").attr("disabled", true)
                } 
                $(".next-page").click(function () {            
                    var newNum = Number(pageNum) + 1; 
                    pageMax = Number(pageMax)
                    if (newNum <= pageMax) {
                        $(".page-number").text(newNum);
                        // Re-render any visble tables
                        ReplaceResultTable();
                    } 
                });
                $(".prev-page").click(function () {
                    var newNum = Number(pageNum) - 1; 
                    pageMax = Number(pageMax)
                    if (newNum >= 0 ) {
                        $(".page-number").text(newNum);
                        // Re-render any visble tables
                        ReplaceResultTable();
                    }
                });
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function ReplaceJobsTable() {
    // If we're not on the jobs page
    if (!$('.job-table-body').length) {
        return;
    }
    
    // Zero out the existing html
    $('.job-table-head').html("")
    $('.job-table-body').html("")

    // Set the field we use as the ID,  this gets referenced when the row is clicked
    var idField = 0;
    // Set the field we use as the progress bar, this is an index as returned via the tablular api
    var pbField = 5;


    // Make the API call to get the values
    var pageNum = $(".page-number").text();

    var url = API_ROUTE + "/jobs?table=true&page="+ pageNum;
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);;
                return;
            }

            response.json().then(function (data) {
                // Render the table headers
                $.each(data['result']['fields'], function(k, v) {
                    $('.job-table-head').append('<th scope="col">' + v + '</th>');
                }); 
                
                // Render the rows
                $.each(data['result']['rows'], function(k, v) { 
                    // Se the row data-target as the ID of the job, to be used as the link to the next page.
                    var targetId = v[0];
                    rowId = "jobs-row-" + k;
                    $('.job-table-body').append('<tr class="clickable-row" data-target="'+ targetId +'" id="' + rowId + '">')
                    
                    // Register the click handlers for the row object
                    $('#'+rowId).click(function() {
                        window.location.href='/jobs/'+targetId;
                    })
                    // Render the row data
                    $.each(v, function(k, v) {
                        if (k === pbField) {
                            pb = new ProgressBar(0, 100); 
                            $("#"+rowId).append('<td>' + pb.render(v) + '</td>');
                        } else{
                            $("#"+rowId).append('<td>' + v + '</td>');
                        }
                    }); 
                }); 

            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function ClickListAddButton(obj) {
    /* Clicking the little + button next to a list type input */
    console.log("clicked")
    var targetList = "#" + $(obj).attr('data-target');
    
    inputs = [];
    // Get the count of current input fields
    $(targetList + " :input").each(function () {
        inputs.push(this);

    })
    // Add a new input when the button is clicked.
    //inputHtml = '<input class="form-control mb-2 l-input" name="' + $(inputs[0]).attr('name') + "-" + inputs.length + '">'
    inputHtml = $(inputs[0]).clone();
    $(targetList).append(inputHtml);   

}

function ClickAddButton(obj) {
    var moduleType = $(obj).attr('data-type');
    var moduleName = $(obj).attr('data-module');
    var formId = "#new-item-form";

    var data = {}
    // Normal input items
    $(formId + " .n-input").each(function () {
        data[$(this).attr('name')] = $(this).val()
    })

    // List type input items
    $(formId + " .l-input").each(function () {
        // Init the lists as part of the map
        data[$(this).attr('data-list')] = [];
    })

    $(formId + " .l-input").each(function () {
        data[$(this).attr('data-list')].push($(this).val())
    })

    data['type'] = moduleName;

    console.log(data['type'])

    fetch(API_CONFIG_ROUTE + "/" + moduleType, {
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
    var moduleName = $(obj).attr('data-module');
    var itemName = $(obj).attr('data-name');

    var url = API_CONFIG_ROUTE + "/" + moduleType + "/" + moduleName + "/spec?as_html=true&from="+itemName;
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.text().then(function (data) {
                $(".new-config").html(data);

                $(".save").click(function () {
                    ClickAddButton(this)
                });
            
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}

function ClickRunButton() {

    inputData = ScanSpecSettings();
    console.log(inputData);
    obj = ".run"
    fetch(API_ROUTE + "/run", {
        method: 'POST',
        body: JSON.stringify(inputData),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);

                $(obj).text("Failed!");
                $(obj).addClass("btn-danger").removeClass("btn-primary")
                return;
            }

            // Examine the text in the response
            response.json().then(function (data) {
                // If the operation is gucci gang gucci gang gucci gang
                if (data['status'] === "started") {
                    $(obj).text(data['id']);
                    $(obj).addClass("btn-success").removeClass("btn-primary")

                }
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

    var url = API_CONFIG_ROUTE + "/" + moduleType + "/" + moduleName;
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
    var jobName = $(".spec-name").val()

    var data = {
        'spec': {
            'inputs': [inputName],
            'modules': []
        }
    }; 

    if (jobName) {
        data['name'] = jobName;
    }
    
    items.each(function () {
        data['spec']['modules'].push($(this).text())
    })

    if (data['spec']['modules'].length > 0) {
        $(".run").removeClass("d-none")
    }
    return(data);
}