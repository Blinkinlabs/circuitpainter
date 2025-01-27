function lotus_leds() {
    console.log('ok');

    function refreshSvg() {
        let leds = parseInt(document.getElementById('param-leds').value);
        let radius = parseInt(document.getElementById('param-radius').value);
        let ledRadiusPercent = parseFloat(document.getElementById('param-led-radius-percent').value);

        let topSvg = document.getElementById("svg-preview");
        // topSvg.src = "/lotus_leds/svg/" + leds;
        topSvg.src = "/lotus_leds/svg?leds=" + leds + "&radius=" + radius + "&led_radius_percent=" + ledRadiusPercent;
    }

    document.getElementById('param-leds').addEventListener('change', refreshSvg );
    document.getElementById('param-radius').addEventListener('change', refreshSvg );
    document.getElementById('param-led-radius-percent').addEventListener('change', refreshSvg );
    refreshSvg();
}