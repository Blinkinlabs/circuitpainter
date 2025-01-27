from flask import Flask, request, render_template, Response, make_response
from lotus_leds import lotus_leds

app = Flask(__name__)

@app.route('/lotus_leds/svg', methods=['GET'])
def route_lotus_leds_svg():
    leds = int(request.args.get('leds'))
    radius = int(request.args.get('radius'))
    led_radius_percent = float(request.args.get('led_radius_percent'))

    painter = lotus_leds(leds=leds, radius=radius, led_radius_percent=led_radius_percent)

    tempname = "testtest"
    painter.export_svg(tempname)

    with open(f'{tempname}.svg','r') as f:
        svg = f.read()

    return Response(svg, mimetype='image/svg+xml', status=200)

@app.route('/lotus_leds', methods=['GET'])
def route_lotus_leds():
    return render_template('lotus_leds.html')

if __name__ == '__main__':
    app.run()
