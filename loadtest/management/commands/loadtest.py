from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import json


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--submit',
                    action='store_true',
                    dest='cchq_url',
                    help='Causes Load Tester to submit cases to the specified url.'),
        make_option('-f', '--specfile',
                    action='store',
                    default=None,
                    dest='specfile',
                    help='The specfile is used to indicate property names and values. NUM_PROPERTIES takes precedence over this file. In other words, if there are 50 properties listed in the spec file but NUM_PROPERTIES is set to 20: Load Tester will only take the first 20 properties listed in the file for case generation. If --specfile is used, NUM_PROPERTIES is optional (if it is not present all properties in the spec file will be used).',
        ),
        make_option('-d', '--dumppath',
                    action='store',
                    dest='dumppath',
                    help='By default all cases will be generated and submitted to HQ. To prevent this behaviour and just save the files to disk, use this option. FOLDER_FOR_SUBMISSIONS indicates where the instances should be saved.'
            ),
        make_option('-q', '--quiet',
                    action='store_true',
                    dest='verbose',
                    default=False,
                    help='Not interested in a play-by-play? Use this to simply get a summary note at the end of the run.',
        ),
        make_option('--use-version-two',
                    action='store_true',
                    dest='usev2',
                    default=False,
                    help='Use CaseXML Version 2 style Case Blocks.'
        ),
    )

    def p(self,txt):
        if not txt:
            txt = ''
        self.stdout.write('%s\n' % txt)

    help = "The purpose of this tool is to generate and send multiple case properties, in multiple forms, and submit them to the commcarehq instance of your choice.  The tool can be set to generate case data at random (the property names and values being generated at random) or to make use of a definition file (JSON) to generate a specific set of keys and values. \n\nSee README.rst for more information."
    args = 'NUM_CASES NUM_PROPERTIES'

    spec = None

    def load_specfile(self, specpath):
        """
        Parse file specified by specpath and parse with json lib.
        """
        f = open(specpath,'r')
        lines = ''.join(f.readlines())
        f.close()
        self.spec = json.loads(lines)

    def is_specfile_explicit(self):
        """
        Checks to see if the 'explicit' flag in the specfile has been set.
        """
        if not self.spec.has_key('explicit'):
            raise CommandError("JSON Specfile MUST contain an 'explicit' flag!")
        return self.spec["explicit"]



    def handle(self, *args, **options):
        self.p(args)
        self.p(options)
        if len(args) != 2 and not options["specfile"]:
            raise CommandError("Must Specify both NUM_CASES and NUM_PROPERTIES arguments OR a specfile")

        if options["specfile"]:
            self.load_specfile(options["specfile"])

        if len(args) != 1  and self.spec and not self.is_specfile_explicit():
            raise CommandError("Must include NUM_CASES arg when JSON specfile is not in Explicit mode")





