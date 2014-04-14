import os

from css import CssFormat
from base import Option


class ScssFormat(CssFormat):

    extension = 'scss'
    options_group = 'SCSS format options'
    options = [
        Option(
            '--scss',
            dest='scss_dir', argtype=Option.STORE_TRUE, environ='GLUE_SCSS',
            default=False,
            metavar='DIR',
            help='Generate SCSS files and optionally where'
        ),
        Option(
            '--scss-template',
            dest='scss_template', argtype=Option.REQUIRED, environ='GLUE_SCSS_TEMPLATE',
            default=None,
            metavar='DIR',
            help='Template to use to generate the SCSS output.'
        ),
    ]
