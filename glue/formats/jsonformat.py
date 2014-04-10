import os
import json
import codecs

from base import BaseJSONFormat, Option


class JSONFormat(BaseJSONFormat):

    extension = 'json'
    build_per_ratio = True
    options_group = 'JSON format options'
    options = [
        Option(
            '--json',
            dest='json_dir', type=Option.STORE_TRUE, environ='GLUE_JSON',
            default=False,
            metavar='DIR',
            help='Generate JSON files and optionally where'
        ),
        Option(
            '--json-format',
            dest='json_format', type=Option.REQUIRED, environ='GLUE_JSON_FORMAT',
            choices=['array', 'hash'],
            default='array',
            metavar='NAME',
            help='JSON structure format (array, hash)'
        ),
    ]

    def get_context(self, *args, **kwargs):
        context = super(JSONFormat, self).get_context(*args, **kwargs)

        frames = dict([[i['filename'], {'filename': i['filename'],
                                        'frame': {'x': i['x'],
                                                  'y': i['y'],
                                                  'w': i['width'],
                                                  'h': i['height']},
                                        'rotated': False,
                                        'trimmed': False,
                                        'spriteSourceSize': {'x': i['x'],
                                                             'y': i['y'],
                                                             'w': i['width'],
                                                             'h': i['height']},
                                        'sourceSize': {'w': i['original_width'],
                                                       'h': i['original_height']}}] for i in context['images']])

        data = dict(frames=None, meta={'version': context['version'],
                                       'hash': context['hash'],
                                       'name': context['name'],
                                       'sprite_path': context['sprite_path'],
                                       'sprite_filename': context['sprite_filename'],
                                       'width': context['width'],
                                       'height': context['height']})

        if self.sprite.config['json_format'] == 'array':
            data['frames'] = frames.values()
        else:
            data['frames'] = frames

        return data
