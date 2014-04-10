from distutils.cmd import Command


class compile_sprite(Command):


    description = 'Compile sprite'
    user_options = [
        ('source=', 's',
         'Source path'),
        ('output=', 'o',
         'Output path'),
        ('quiet', 'q',
         'Suppress all normal output'),
        ('recursive', 'r',
         'Read directories recursively and add all '\
         'the images to the same sprite.'),
        ('force', 'r',
         'Force glue to create every sprite image and '\
         'metadata file even if they already exists in '\
         'the output directory.'),
        ('follow-links', None,
         'Follow symbolic links.'),
        ('project', None,
         'Generate sprites for multiple folders'),
    ]
    boolean_options = ['quiet', 'recursive', 'follow_links', 'force', 'project']

    def initialize_options(self):
        self.source = None
        self.output = None
        self.quiet = False
        self.recursive = False
        self.force = False
        self.follow_links = False
        self.project = False

    def finalize_options(self):
        pass

    def run(self):
        pass
