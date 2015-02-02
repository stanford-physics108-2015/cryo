function OpenImage(item_title, item_url) {
    var item_url
    var options = {
        title: item_title,
        url: item_url,
        autoSize: true,
        allowMaximize: false,
        dialogReturnValueCallback: DialogCallback
    };
    SP.UI.ModalDialog.showModalDialog(options);
}
function DialogCallback(dialogResult, returnValue) { }