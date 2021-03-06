(function($, BD) {
    "use strict";

    $(function() {
        var locale = $('html').attr('lang');
        var gaBubbleOpen = ['_trackPageview', interpolate('/%s/products/firefox/up-to-date-download', [locale])];

        $('.download-firefox .download-button').on('click', function(ev) {
            var $this = $(this);
            var latestVersion = $this.data('latest-version');

            if ((BD.version >= latestVersion) && (BD.browser == 'fx')) {
                ev.stopPropagation();
                ev.preventDefault();
                $this.siblings('.help-bubble').show();
                _gaq.push(gaBubbleOpen);
            }
        });
    });
})(jQuery, BrowserDetect);
