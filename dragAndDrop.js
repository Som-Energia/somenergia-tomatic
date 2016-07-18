// <td class='carles'><span>Carles</span></td>
// ...
//<div class="extension aleix"><span class="event" id="aleix" draggable="true">Aleix</span><br/>3053</div>
$(document).ready(function () {
    $('.event').on("dragstart", function (event) {
        var dt = event.originalEvent.dataTransfer;
        dt.setData('Text', $(this).attr('id'));
    });
    $('table td').on("dragenter dragover drop", function (event) {
        event.preventDefault();
        if (event.type === 'drop') {
            var data = event.originalEvent.dataTransfer.getData('Text', $(this).attr('id'));
            
            de = $('#' + data).clone();//.detach();
            if (event.originalEvent.target.tagName === "SPAN") {
            		var parent = $(event.originalEvent.target).parent();
                var parentClass = parent.attr('class');
                parent.toggleClass(data);
                parent.toggleClass(parentClass,false);
                $(event.originalEvent.target).replaceWith(de);
            }
            else {
                de.appendTo($(this));
            }
        };
    });
})
