var WebPartElementID = "ctl00_MSO_ContentDiv";
//Hide print link in printer friendly page view
if (document.getElementById("print"))
    document.getElementById("print").style.display = 'none';
if (document.getElementById("NoDisplayInPrint"))
    document.getElementById("NoDisplayInPrint").style.display = 'none';
if (document.getElementById("NoDisplayInPrint2"))
    document.getElementById("NoDisplayInPrint2").style.display = 'none';
if (document.getElementById("NoDisplayInPrint3"))
    document.getElementById("NoDisplayInPrint3").style.display = 'none';
if (document.getElementById("print"))
    document.getElementById("print").style.visibility = 'hidden';
if (document.getElementById("NoDisplayInPrint"))
    document.getElementById("NoDisplayInPrint").style.visibility = 'hidden';
if (document.getElementById("NoDisplayInPrint2"))
    document.getElementById("NoDisplayInPrint2").style.visibility = 'hidden';
if (document.getElementById("NoDisplayInPrint2"))
    document.getElementById("NoDisplayInPrint3").style.visibility = 'hidden';
//document.body.style.backgroundColor = "white";

//Function to print Web Part
function PrintWebPart() {
    var bolWebPartFound = false;
    //var currentPage = document.location.href;
    if (document.getElementById != null) {
        //Create html to print in new window
        var PrintingHTML = '<HTML>\n<HEAD>\n';
        //Take data from Head Tag
        if (document.getElementsByTagName != null) {
            var HeadData = document.getElementsByTagName("HEAD");
            if (HeadData.length > 0)
                PrintingHTML += HeadData[0].innerHTML;
        }
        PrintingHTML += '\n</HEAD>\n<BODY>\n';
        var WebPartData = document.getElementById(WebPartElementID);
        if (WebPartData != null) {
            PrintingHTML += WebPartData.innerHTML;
            bolWebPartFound = true;
        }
        else {
            bolWebPartFound = false;
            alert('Cannot Find Web Part');
        }
    }
    PrintingHTML += '\n</BODY>\n</HTML>';
    //Open new window to print
    if (bolWebPartFound) {
        var PrintingWindow = window.open("", "PrintWebPart", "toolbar,width=800,height=600,scrollbars,resizable,menubar");
        PrintingWindow.document.open();
        PrintingWindow.document.write(PrintingHTML);
        // Open Print Window
        PrintingWindow.print();
    }
}
