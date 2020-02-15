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

    $(".select-tagp").click(function () {
        SelectTagpButton(this);
        ScanSpecSettings();
    });

    $(".select-output").click(function () {
        SelectOutputButton(this);
        ScanSpecSettings();
    });

    $(".select-spec").click(function () {
        SelectSpecButton(this);
    });

    $(".run").click(function () {
        ClickRunButton()
    });

    // Render the jobs table
    ReplaceJobsTable();
    // Render the job result table
    ReplaceResultTable();
    /*
    Tag config stuff
    */
    $(".pick-job").click(function () {
        ClickChooseJob(this)
    });
    $(".add-list-tag").click(function() {
        ClickAddTagToList(this)
    })

    $(".save-tag-list").click(function() {
        ClickSaveTagList(this)
    })
    
    // Graphs n stuff
    RenderTagGraphs();

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


function ClickHostCard(obj) {
    $(".mods", obj).toggle();
}

function ClickJobRow(obj) {
    console.log("here")
    window.location.href = $(obj).attr("data-target");
}

function SelectSpecButton(obj) {
    var specid = $(obj).attr('data-target');

    var url = API_ROUTE + "/specs/" + specid
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.json().then(function (data) {
                SetInput(data['spec']['inputs'][0])
                $(".selected-module-container").html("")

                $(data['spec']['modules']).each(function () {
                    // Zero out the module html before re-inserting
                    SetModules(this);
                })
                if ('tag_policy' in data['spec'] ) {
                    SetTagp(data['spec']['tag_policy']);
                }
                ScanSpecSettings();
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function ClickAddTagToList(obj) {
    var target = $(obj).attr('data-target');

    $("#"+target).appendTo(".selected-tags")
    $(obj).text("-");
    $(obj).removeClass("btn-primary");
    $(obj).addClass("btn-danger")
    $(obj).click(function() {
        var target = $(obj).attr('data-target');

        $("#"+target).appendTo(".tags-available")

        $(obj).text("+");
        $(obj).removeClass("btn-danger")
        $(obj).addClass("btn-primary");
        $(this).click(
            function() {
                ClickAddTagToList(this);
            }
        )

    })
}

function ClickSaveTagList(obj) {
    data = {
        "tags": []
    }
    $(".selected-tags > div > input").each(function() {
        data["tags"].push(($(this).val()))
    })

    data["name"] = $(".name").val();
    fetch(API_CONFIG_ROUTE + "/taglist", {
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

function ClickAddTagButton() {
    $(".new-config").toggle();

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

function RenderTagGraphs() {
    if (!$('#tag-stats').length) {
        return;
    }

    var res = top.location.pathname.split("/");
    var jobID = res[2]

    var url = API_ROUTE + "/jobs/" + jobID + "/graph"
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.json().then(function (rdata) {
                var ctx = $("#tag-stats")
                var statsChart = new Chart(ctx, {
                    type: 'pie',
                    data: rdata,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                    }
                })
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

                /*
                Results page stuff
                */
                $(".clickable-card").click(function (){
                    ClickHostCard(this)
                })

                
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function ReplaceJobsTable() {

    if (!$('.jobs').length) {
        return;
    }


    // Make the API call to get the values
    var pageNum = $(".page-number").text();

    var url = API_ROUTE + "/jobs?table=true&as_html=true&page="+ pageNum;
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.text().then(function (data) {
                $('.jobs').html(data);

                var pageNum = $(".page-number").text();
                var pageMax = $(".page-max").text();
                console.log(pageMax)

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
                        ReplaceJobsTable();
                    } 
                });
                $(".prev-page").click(function () {
                    var newNum = Number(pageNum) - 1; 
                    pageMax = Number(pageMax)
                    if (newNum >= 0 ) {
                        $(".page-number").text(newNum);
                        // Re-render any visble tables
                        ReplaceJobsTable();
                    }
                });

                $(".clickable-row").click(function (){
                    ClickJobRow(this)
                })
                
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
                $(obj).addClass("btn-danger").removeClass("btn-primary")

                return;
            }

            // Examine the text in the response
            response.json().then(function (data) {
                // If the operation is gucci gang gucci gang gucci gang
                if (data['status'] === 0) {
                    $(obj).text("Added!");
                    $(obj).addClass("btn-success").removeClass("btn-primary")
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
    obj = ".run"
    $(obj).attr("disabled", true)

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
                    window.location.href = "/jobs/"+data['id'];
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

function SetInput(moduleName) {
    /* Use the name, which'll be used by teh spec, as well as display it. */
    var selectedHTML = `<h3 class='p-3 h1-input-selected input-value'>` +  moduleName + `</h3>`

    /* Make the list invisible */
    $(".input-dropdown").toggle()
    /* Modify the card appearance to show it's selected */
    $(".input-card").html(selectedHTML)
    $(".input-card").addClass("card-input-filled")
    // Make the next step visible
    $("#fadein-1").fadeTo( "slow" , 1, function() {
    }); 

    $("#input-step").addClass("active");
}

function SelectInputButton(obj) {
    var moduleName = $(obj).attr('data-name');

    SetInput(moduleName);
}

function SetOutput(moduleName) {
    /* Use the name, which'll be used by teh spec, as well as display it. */
    var selectedHTML = `<h3 class='p-3 h1-input-selected output-value'>` +  moduleName + `</h3>`

    /* Make the list invisible */
    $(".output-dropdown").toggle()
    /* Modify the card appearance to show it's selected */
    $(".output-card").html(selectedHTML)
    $(".output-card").addClass("card-input-filled")
}

function SelectOutputButton(obj) {
    var moduleName = $(obj).attr('data-name');

    SetOutput(moduleName)
}

function SetTagp(tagpName) {
    /* Use the name, which'll be used by teh spec, as well as display it. */
    var selectedHTML = `<h3 class='p-3 h1-input-selected tagp-value'>` +  tagpName + `</h3>`

    /* Make the list invisible */
    $(".tagp-dropdown").toggle()
    /* Modify the card appearance to show it's selected */
    $(".tagp-card").html(selectedHTML)
    $(".tagp-card").addClass("card-input-filled")

    $("#tagp-step").addClass("active");

}

function SelectTagpButton(obj) {
    var tagpName = $(obj).attr('data-name');

    SetTagp(tagpName)

}


function SetModules(moduleName) {
    $(".module-dropdown").text("Pick another module...")
    /* Use the name, which'll be used by teh spec, as well as display it. */
    var selectedHTML = `<h3 class='p-3 h1-module-selected module-value'>` +  moduleName + `</h3>`
    $(".selected-module-container").append(selectedHTML)

    $("#fadein-2").fadeTo( "slow" , 1, function() {
    }); 

    $("#fadein-3").fadeTo( "slow" , 1, function() {
    }); 

    $("#module-step").addClass("active");


}

function SelectModuleButton(obj) {
    var moduleName = $(obj).attr('data-name');

    SetModules(moduleName)

}

function ScanSpecSettings () {
    /* Scans the spec page to ensure the user as selected an input, at least one module, and an output */
    var inputName = $(".input-value").text(); 
    var jobName = $(".spec-name").val()
    var tagpName = $(".tagp-value").text(); 
    var outputName = $(".output-value").text(); 
    var data = {
        'spec': {
            'inputs': [inputName],
            'modules': []
        }
    }; 


    if (jobName) {
        data['name'] = jobName;
    }
    
    $(".module-value").each(function () {
        data['spec']['modules'].push($(this).text())
    })

    if (data['spec']['modules'].length > 0) {
        $(".run").removeClass("d-none")
    }
    if (tagpName) {
        data['spec']['tag_policy'] = tagpName
    }
    if (outputName) {
        data['spec']['output'] = outputName
    } 
    if ( $("#save-spec").is(":checked") ) {
        data['save'] = true
    } else {
        data['save'] = false
    }
    console.log(data)
    return(data);
}

function ClickChooseJob(obj) {
    var jobId  = $(obj).attr('data-target');
    $("#dropdownMenuButton").text(jobId)
    $("#dropdownMenuButton").button('toggle')
    var url = API_ROUTE + "/jobs/"+jobId+"/tag_spec?as_html=true";
    fetch(url).then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.text().then(function (data) {
                $(".job-display").html(data);

                var cp = new ColorPicker();
                cp.Register();

                $(".save-tag").click(function () {
                    ClickSaveTagButton(this)
                });
            });
        }
    )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function ClickSaveTagButton(obj) {
    var formId = "#new-item-form";

    var data = {
        name: '',
        match: {},
        match_any: false
    }
    // Normal input items
    // Name
    data['name'] = $(".name").val(); 
    // Description
    data['description'] = $(".descr").val(); 
    // Tag color
    data['color'] = $(".c-input").val(); 

    // Match criteria
    $(formId + " .m-input").each(function () {
        var v = $(this).val();
        if (v != "") {
            data['match'][$(this).attr('name')] = $(this).val()
        }
    })
    fetch(API_CONFIG_ROUTE + "/tags", {
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
                $(obj).addClass("btn-danger").removeClass("btn-primary")
                return;
            }

            // Examine the text in the response
            response.json().then(function (data) {
                // If the operation is gucci gang gucci gang gucci gang
                if (data['status'] === 0) {
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

class ColorPicker {
    ClickPickColor(obj) {
        var color = $(obj).attr('data-value'); 
        $(".color-picker-button").css('background-color', color)
        $(".c-input").val(color)
    }
    ClickColorPicker() {
        $('.color-picker-colors').toggle();
    }

    Register() {
        var cl = this;
        $(".color-picker-button").click(function () {
            cl.ClickColorPicker(this);
        });

        $(".color-button").click(function () {
            cl.ClickPickColor(this);
        });
    }
}
