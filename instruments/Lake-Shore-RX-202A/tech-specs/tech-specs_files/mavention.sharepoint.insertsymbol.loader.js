/// <reference path="c:\Program Files\common Files\microsoft Shared\web Server Extensions\14\TEMPLATE\LAYOUTS\MicrosoftAjax.js" />
/// <reference path="c:\Program Files\common Files\microsoft Shared\web Server Extensions\14\TEMPLATE\LAYOUTS\1033\INIT.debug.js" />
/// <reference path="c:\Program Files\common Files\microsoft Shared\web Server Extensions\14\TEMPLATE\LAYOUTS\SP.debug.js" />

SP.SOD.executeOrDelayUntilScriptLoaded(function () {
    SP.SOD.executeOrDelayUntilScriptLoaded(function () {
        var ctx = SP.ClientContext.get_current();
        var site = ctx.get_site();
        ctx.load(site);
        ctx.executeQueryAsync(Function.createDelegate(this, function (sender, args) {
            var pageComponentScriptUrl = SP.Utilities.UrlBuilder.urlCombine(site.get_url(), "Style Library/Mavention/InsertSymbol/Mavention.SharePoint.InsertSymbol.PageComponent.js");
            SP.SOD.registerSod('mavention.sharepoint.insertsymbol.pagecomponent.js', pageComponentScriptUrl);
            SP.SOD.execute('mavention.sharepoint.insertsymbol.pagecomponent.js', 'Mavention.SharePoint.InsertSymbol.PageComponent.initialize');
        }));
    }, "cui.js");
}, "sp.js");