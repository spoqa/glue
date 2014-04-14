import os

from css import CssFormat
from base import Option


class LessFormat(CssFormat):

    extension = 'less'
    template = u"""
        /* glue: {{ version }} hash: {{ hash }} */
        {% for image in images %}.{{ image.label }}{{ image.pseudo }}{%- if not image.last %}, {%- endif %}{%- endfor %}{
            background-image:url('{{ sprite_path }}');
            background-repeat:no-repeat;
            -webkit-background-size: {{ width }}px {{ height }}px;
            -moz-background-size: {{ width }}px {{ height }}px;
            background-size: {{ width }}px {{ height }}px;
            {% for r, ratio in ratios.iteritems() %}
            @media screen and (-webkit-min-device-pixel-ratio: {{ ratio.ratio }}), screen and (min--moz-device-pixel-ratio: {{ ratio.ratio }}),screen and (-o-min-device-pixel-ratio: {{ ratio.fraction }}),screen and (min-device-pixel-ratio: {{ ratio.ratio }}),screen and (min-resolution: {{ ratio.ratio }}dppx){
                background-image:url('{{ ratio.sprite_path }}');
            }
            {% endfor %}
        }
        {% for image in images %}
        .{{ image.label }}{{ image.pseudo }}{
            background-position:{{ image.x ~ ('px' if image.x) }} {{ image.y ~ ('px' if image.y) }};
            width:{{ image.width }}px;
            height:{{ image.height }}px;
        }
        {% endfor %}
        """
    options_group = 'LESS format options'
    options = [
        Option(
            '--less',
            dest='less_dir', argtype=Option.STORE_TRUE, environ='GLUE_LESS',
            default=False,
            metavar='DIR',
            help='Generate LESS files and optionally where'
        ),
        Option(
            '--less-template',
            dest='less_template', argtype=Option.REQUIRED, environ='GLUE_LESS_TEMPLATE',
            default=None,
            metavar='DIR',
            help='Template to use to generate the LESS output.'
        ),
    ]
