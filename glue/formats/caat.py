import os

from base import BaseJSONFormat, Option


class CAATFormat(BaseJSONFormat):

    extension = 'json'
    build_per_ratio = True
    options_group = 'JSON format options'
    options = [
        Option(
            '--caat',
            dest='caat_dir', argtype=Option.STORE_TRUE, environ='GLUE_CAAT',
            default=False,
            metavar='DIR',
            help='Generate CAAT files and optionally where'
        ),
    ]

    def get_context(self, *args, **kwargs):
        context = super(CAATFormat, self).get_context(*args, **kwargs)

        data = dict(sprites={}, meta={'version': context['version'],
                                      'hash': context['hash'],
                                      'sprite_filename': context['sprite_filename'],
                                      'width': context['width'],
                                      'height': context['height']})
        for i in context['images']:
            data['sprites'][i['filename']] = {"x" : i['abs_x'],
                                              "y" : i['abs_y'],
                                              "width" : i['width'],
                                              "height" : i['height']}
        return data
