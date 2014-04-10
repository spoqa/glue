import re
import os
import codecs

from glue import __version__
from base import JinjaTextFormat, Option

from ..exceptions import ValidationError


class CssFormat(JinjaTextFormat):

    extension = 'css'
    camelcase_separator = 'camelcase'
    css_pseudo_classes = set(['link', 'visited', 'active', 'hover', 'focus',
                              'first-letter', 'first-line', 'first-child',
                              'before', 'after'])

    template = u"""
        /* glue: {{ version }} hash: {{ hash }} */
        {% for image in images %}.{{ image.label }}{{ image.pseudo }}{%- if not image.last %},{{"\n"}}{%- endif %}{%- endfor %} {
            background-image: url('{{ sprite_path }}');
            background-repeat: no-repeat;
        }
        {% for image in images %}
        .{{ image.label }}{{ image.pseudo }} {
            background-position: {{ image.x ~ ('px' if image.x) }} {{ image.y ~ ('px' if image.y) }};
            width: {{ image.width }}px;
            height: {{ image.height }}px;
        }
        {% endfor %}{% for r, ratio in ratios.iteritems() %}
        @media screen and (-webkit-min-device-pixel-ratio: {{ ratio.ratio }}), screen and (min--moz-device-pixel-ratio: {{ ratio.ratio }}), screen and (-o-min-device-pixel-ratio: {{ ratio.fraction }}), screen and (min-device-pixel-ratio: {{ ratio.ratio }}), screen and (min-resolution: {{ ratio.ratio }}dppx) {
            {% for image in images %}.{{ image.label }}{{ image.pseudo }}{% if not image.last %},{{"\n"}}    {% endif %}{% endfor %} {
                background-image: url('{{ ratio.sprite_path }}');
                -webkit-background-size: {{ width }}px {{ height }}px;
                -moz-background-size: {{ width }}px {{ height }}px;
                background-size: {{ width }}px {{ height }}px;
            }
        }
        {% endfor %}
        """

    options_group = 'CSS format options'
    options = [
        Option(
            '--css',
            dest='css_dir', type=Option.STORE_TRUE, environ='GLUE_CSS',
            default=False,
            metavar='DIR',
            help='Generate CSS files and optionally where'
        ),
        Option(
            '--namespace',
            dest='css_namespace', type=Option.REQUIRED, environ='GLUE_CSS_NAMESPACE',
            default='sprite',
            help='Namespace for all css classes (default: sprite)'
        ),
        Option(
            '--sprite-namespace',
            dest='css_sprite_namespace', type=Option.REQUIRED, environ='GLUE_CSS_SPRITE_NAMESPACE',
            default='{sprite_name}',
            help='Namespace for all sprites (default: {sprite_name})'
        ),
        Option(
            ('-u', '--url'),
            dest='css_url', type=Option.REQUIRED, environ='GLUE_CSS_URL',
            default='',
            help='Prepend this string to the sprites path'
        ),
        Option(
            '--cachebuster',
            dest='css_cachebuster', type=Option.STORE_TRUE, environ='GLUE_CSS_CACHEBUSTER',
            default=False,
            help="Use the sprite's sha1 first 6 characters as a queryarg everytime that file is referred from the css"
        ),
        Option(
            '--cachebuster-filename',
            dest='css_cachebuster_filename', type=Option.STORE_TRUE, environ='GLUE_CSS_CACHEBUSTER',
            default=False,
            help="Append the sprite's sha first 6 characters to the output filename"
        ),
        Option(
            '--cachebuster-filename-only-sprites',
            dest='css_cachebuster_only_sprites', type=Option.STORE_TRUE, environ='GLUE_CSS_CACHEBUSTER_ONLY_SPRITES',
            default=False,
            help='Only apply cachebuster to sprite images.'
        ),
        Option(
            '--separator',
            dest='css_separator', type=Option.REQUIRED, environ='GLUE_CSS_SEPARATOR',
            default='-',
            metavar='SEPARATOR',
            help=("Customize the separator used to join CSS class names."
                 "If you want to use camelCase use 'camelcase' as separator.")
        ),
        Option(
            '--pseudo-class-separator',
            dest='css_pseudo_class_separator', type=Option.REQUIRED, environ='GLUE_CSS_PSEUDO_CLASS_SEPARATOR',
            default='__',
            metavar='SEPARATOR',
            help=('Customize the separator glue will use in order to'
                  'determine the pseudo classes included into filenames.')
        ),
        Option(
            '--css-template',
            dest='css_template', type=Option.REQUIRED, environ='GLUE_CSS_TEMPLATE',
            default=None,
            metavar='DIR',
            help='Template to use to generate the CSS output.'
        ),
        Option(
            '--no-css',
            dest='generate_css', type=Option.STORE_FALSE, environ='GLUE_GENERATE_CSS',
            default=True,
            help="Don't genereate CSS files."
        ),

    ]

    @classmethod
    def apply_parser_contraints(cls, parser, options):
        cachebusters = (options.css_cachebuster, options.css_cachebuster_filename, options.css_cachebuster_only_sprites)
        if sum(cachebusters) > 1:
            parser.error("You can't use --cachebuster, --cachebuster-filename or --cachebuster-filename-only-sprites at the same time.")

    def needs_rebuild(self):
        hash_line = '/* glue: %s hash: %s */\n' % (__version__, self.sprite.hash)
        try:
            with codecs.open(self.output_path(), 'r', 'utf-8-sig') as existing_css:
                first_line = existing_css.readline()
                assert first_line == hash_line
        except Exception:
            return True
        return False

    def validate(self):
        class_names = [':'.join(self.generate_css_name(i.filename)) for i in self.sprite.images]
        if len(set(class_names)) != len(self.sprite.images):
            dup = [i for i in self.sprite.images if class_names.count(':'.join(self.generate_css_name(i.filename))) > 1]
            duptext = '\n'.join(['\t{0} => .{1}'.format(os.path.relpath(d.path), ':'.join(self.generate_css_name(d.filename))) for d in dup])
            raise ValidationError("Error: Some images will have the same class name:\n{0}".format(duptext))
        return True

    def output_filename(self, *args, **kwargs):
        filename = super(CssFormat, self).output_filename(*args, **kwargs)
        if self.sprite.config['css_cachebuster_filename']:
            return '{0}_{1}'.format(filename, self.sprite.hash)
        return filename

    def get_context(self, *args, **kwargs):

        context = super(CssFormat, self).get_context(*args, **kwargs)

        # Generate css labels
        for image in context['images']:
            image['label'], image['pseudo'] = self.generate_css_name(image['filename'])

        if self.sprite.config['css_url']:
            context['sprite_path'] = '{0}{1}'.format(self.sprite.config['css_url'], context['sprite_filename'])

            for r, ratio in context['ratios'].iteritems():
                ratio['sprite_path'] = '{0}{1}'.format(self.sprite.config['css_url'], ratio['sprite_filename'])

        # Add cachebuster if required
        if self.sprite.config['css_cachebuster']:

            def apply_cachebuster(path):
                return "%s?%s" % (path, self.sprite.hash)

            context['sprite_path'] = apply_cachebuster(context['sprite_path'])

            for r, ratio in context['ratios'].iteritems():
                ratio['sprite_path'] = apply_cachebuster(ratio['sprite_path'])

        return context

    def generate_css_name(self, filename):
        filename = filename.rsplit('.', 1)[0]
        separator = self.sprite.config['css_separator']
        namespace = [re.sub(r'[^\w\-_]', '', filename)]

        # Add sprite namespace if required
        if self.sprite.config['css_sprite_namespace']:
            sprite_name = re.sub(r'[^\w\-_]', '', self.sprite.name)
            sprite_namespace = self.sprite.config['css_sprite_namespace']

            # Support legacy 0.4 format
            sprite_namespace = sprite_namespace.replace("%(sprite)s", "{sprite_name}")
            namespace.insert(0, sprite_namespace.format(sprite_name=sprite_name))

        # Add global namespace if required
        if self.sprite.config['css_namespace']:
            namespace.insert(0, self.sprite.config['css_namespace'])

        # Handle CamelCase separator
        if self.sprite.config['css_separator'] == self.camelcase_separator:
            namespace = [n[:1].title() + n[1:] if i > 0 else n for i, n in enumerate(namespace)]
            separator = ''

        label = separator.join(namespace)
        pseudo = ''

        css_pseudo_class_separator = self.sprite.config['css_pseudo_class_separator']
        if css_pseudo_class_separator in filename:
            pseudo_classes = [p for p in filename.split(css_pseudo_class_separator) if p in self.css_pseudo_classes]

            # If present add this pseudo class as pseudo an remove it from the label
            if pseudo_classes:
                for p in pseudo_classes:
                    label = label.replace('{0}{1}'.format(css_pseudo_class_separator, p), "")
                pseudo = ''.join(map(lambda x: ':{0}'.format(x), pseudo_classes))

        return label, pseudo
