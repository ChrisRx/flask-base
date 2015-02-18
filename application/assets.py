from flask_assets import Environment, Bundle
from webassets.filter import register_filter

from .utils import RiotJS


register_filter(RiotJS)

css = Bundle(
    'components/materialize/dist/css/materialize.min.css',
    'css/main.css',
    'css/fonts.css',
)

js_head = Bundle(
    'components/d3/d3.min.js',
    'components/jquery/dist/jquery.min.js',
    'components/lodash/lodash.js'
)

js_body = Bundle(
    'components/materialize/dist/js/materialize.js',
    'components/riot/riot.js',
    Bundle(
        'js/src/*.js',
    )
)

riot_js = Bundle(
    Bundle(
        'js/src/*.tag',
        filters='riotjs',
        output='js/dist/tags.js'
    )
)

assets = Environment()

assets.register('css_all', css)
assets.register('js_head', js_head)
assets.register('js_body', js_body)
assets.register('riot_js', riot_js)
