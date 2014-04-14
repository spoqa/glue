import os

from PIL import Image as PILImage
from PIL import PngImagePlugin

from glue import __version__
from glue.helpers import round_up, cached_property
from .base import BaseFormat, Option


class ImageFormat(BaseFormat):

    build_per_ratio = True
    extension = 'png'
    options_group = 'Sprite image options'
    options = [
        Option(
            '--img',
            dest='img_dir', argtype=Option.REQUIRED, environ='GLUE_IMG',
            default=True,
            metavar='DIR',
            help='Output directory for img files'
        ),
        Option(
            '--no-img',
            dest='generate_image', argtype=Option.STORE_FALSE, environ='GLUE_GENERATE_IMG',
            default=True,
            help="Don't genereate IMG files."
        ),
        Option(
            ('-c', '--crop'),
            dest='crop', argtype=Option.STORE_TRUE, environ='GLUE_CROP',
            default=False,
            help='Crop images removing unnecessary transparent margins'
        ),
        Option(
            ('-p', '--padding'),
            dest='padding', argtype=Option.REQUIRED, environ='GLUE_PADDING',
            default='0',
            help='Force this padding in all images'
        ),
        Option(
            '--margin',
            dest='margin', argtype=Option.REQUIRED, environ='GLUE_MARGIN',
            default='0',
            help='Force this margin in all images'
        ),
        Option(
            '--png8',
            dest='png8', argtype=Option.STORE_TRUE, environ='GLUE_PNG8',
            default=False,
            help='The output image format will be png8 instead of png32'
        ),
        Option(
            '--ratios',
            dest='ratios', argtype=Option.REQUIRED, environ='GLUE_RATIOS',
            default='1',
            help='Create sprites based on these ratios'
        ),
        Option(
            '--retina',
            dest='ratios', argtype=Option.STORE_CONST, environ='GLUE_RETINA',
            const='2,1',
            default=False,
            help='Shortcut for --ratios=2,1'
        ),
    ]

    def output_filename(self, *args, **kwargs):
        filename = super(ImageFormat, self).output_filename(*args, **kwargs)
        if self.sprite.config['css_cachebuster_filename'] or self.sprite.config['css_cachebuster_only_sprites']:
            return '{0}_{1}'.format(filename, self.sprite.hash)
        return filename

    def needs_rebuild(self):
        for ratio in self.sprite.config['ratios']:
            image_path = self.output_path(ratio)
            try:
                existing = PILImage.open(image_path)
                assert existing.info['Software'] == 'glue-%s' % __version__
                assert existing.info['Comment'] == self.sprite.hash
                continue
            except Exception:
                return True
        return False

    @cached_property
    def _raw_canvas(self):
        # Create the sprite canvas
        width, height = self.sprite.canvas_size
        canvas = PILImage.new('RGBA', (width, height), (0, 0, 0, 0))

        # Paste the images inside the canvas
        for image in self.sprite.images:
            canvas.paste(image.image,
                (round_up(image.x + (image.padding[3] + image.margin[3]) * self.sprite.max_ratio),
                 round_up(image.y + (image.padding[0] + image.margin[0]) * self.sprite.max_ratio)))

        meta = PngImagePlugin.PngInfo()
        meta.add_text('Software', 'glue-%s' % __version__)
        meta.add_text('Comment', self.sprite.hash)

        # Customize how the png is going to be saved
        kwargs = dict(optimize=False, pnginfo=meta)

        if self.sprite.config['png8']:
            # Get the alpha band
            alpha = canvas.split()[-1]
            canvas = canvas.convert('RGB'
                        ).convert('P',
                                  palette=PILImage.ADAPTIVE,
                                  colors=255)

            # Set all pixel values below 128 to 255, and the rest to 0
            mask = PILImage.eval(alpha, lambda a: 255 if a <= 128 else 0)

            # Paste the color of index 255 and use alpha as a mask
            canvas.paste(255, mask)
            kwargs.update({'transparency': 255})
        return canvas, kwargs

    def save(self, ratio):
        width, height = self.sprite.canvas_size
        canvas, kwargs = self._raw_canvas

        # Loop all over the ratios and save one image for each one
        for ratio in self.sprite.config['ratios']:

            # Create the destination directory if required
            if not os.path.exists(self.output_dir(ratio=ratio)):
                os.makedirs(self.output_dir(ratio=ratio))

            image_path = self.output_path(ratio=ratio)

            # If this canvas isn't the biggest one scale it using the ratio
            if self.sprite.max_ratio != ratio:

                reduced_canvas = canvas.resize(
                                    (round_up((width / self.sprite.max_ratio) * ratio),
                                     round_up((height / self.sprite.max_ratio) * ratio)),
                                     PILImage.ANTIALIAS)
                reduced_canvas.save(image_path, **kwargs)
                # TODO: Use Imagemagick if it's available
            else:
                canvas.save(image_path, **kwargs)
