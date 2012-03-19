import os
import uuid
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from loadtest.casegenerator import CaseGenerator
import requests
import json
import copy

def get_or_default(dic, key,default):
    ret = default
    try:
        ret = dic[key]
    except KeyError:
        pass
    return ret

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
        make_option('--cc-version',
                    action='store',
                    dest='cc_version',
                    default='1.0',
                    help='Set the CC CaseXML version you would like to use.  Should be either "1.0" or "2.0"'
        ),
        make_option('--user_id',
                    action='store',
                    dest='user_id',
                    default=None,
                    help='Set the case user ID'
        ),
        make_option('--creator_id',
                    action='store',
                    dest='creator_id',
                    default=None,
                    help='Set the case creator ID'
        ),
        make_option('--owner_id',
                    action='store',
                    dest='owner_id',
                    default=None,
                    help='Set the owner ID'
        ),
        make_option('--case_id',
                    action='store',
                    dest='case_id',
                    default=None,
                    help='Set the Case ID'
        ),
        make_option('--case_type',
                    action='store',
                    dest='case_type',
                    default=None,
                    help='Set the Case Type string'
        ),
        make_option('--case_name',
                    action='store',
                    dest='case_name',
                    default=None,
                    help='Set the Case Name string'
        ),
        make_option('--device_id',
                    action='store',
                    dest='device_id',
                    default=None,
                    help='Set the Device ID uuid'
        ),
        make_option('--external_id',
                    action='store',
                    dest='external_id',
                    default=None,
                    help='Set the External ID'
        ),
        make_option('--form_xmlns',
                    action='store',
                    dest='form_xmlns',
                    default=None,
                    help='Set the XMLNS of the Form Submission'
        ),
        make_option('--form_name',
                    action='store',
                    dest='form_name',
                    default=None,
                    help='Set the "name" attribute on the instance'
        ),
        make_option('--username',
                    action='store',
                    dest='username',
                    default=None,
                    help='Set the submission username (different from user_id?)'
        ),
        make_option('--app_guid',
                    action='store',
                    dest='app_guid',
                    default=None,
                    help='Set the CCHQ Application GUID (for submitting cases to a specific app)'
        ),


    )

    def p(self,txt):
        if not txt:
            txt = ''
        self.stdout.write('%s\n' % str(txt))

    title_string = """
    ################
    CCHQ LOAD TESTER
    ################
    """
    description_string = "The purpose of this tool is to generate and send multiple case properties, in multiple forms, and submit them to the commcarehq instance of your choice.  The tool can be set to generate case data at random (the property names and values being generated at random) or to make use of a definition file (JSON) to generate a specific set of keys and values. \n\nSee README.rst for more information." \
                         "\n\nCCHQ_HOST = URL_DOMAIN of CCHQ host e.g. localhost or http://www.commcarehq.org .  Defaults to 'http://localhost:8000'" \
                         "\nCCHQ_DOMAIN = The domain on commcare that you want to submit to. E.g. 'wvmoz'. Defaults to 'test'"
    help = "%s\n%s" % (title_string,description_string)
    args = 'NUM_CASES NUM_PROPERTIES [CCHQ_HOST] [CCHQ_DOMAIN]'

    spec = None

    def parse_spec_opts(self):
        if self.verbosity >= 1:
            self.p('Parsing Specfile...')
        s = self.spec
        self.options["creator_id"] = get_or_default(s,"creator_id", self.options["creator_id"])
        self.options["owner_id"] = get_or_default(s, "owner_id", self.options["owner_id"])
        self.options["case_id"] = get_or_default(s, "case_id", self.options["case_id"])
        self.options["case_type"] = get_or_default(s, "case_type", self.options["case_type"])
        self.options["case_name"] = get_or_default(s, "case_name", self.options["case_name"])
        self.options["device_id"] = get_or_default(s, "device_id", self.options["device_id"])
        self.options["external_id"] = get_or_default(s, "external_id", self.options["external_id"])
        self.options["form_xmlns"] = get_or_default(s, "form_xmlns", self.options["form_xmlns"])
        self.options["form_name"] = get_or_default(s, "form_name", self.options["form_name"])
        self.options["username"] = get_or_default(s, "username", self.options["username"])
        self.options["user_id"] = get_or_default(s, "user_id", self.options["user_id"])
        self.options["cc_version"] = get_or_default(s, "cc_version", self.options["cc_version"])
        self.options["verbosity"] = get_or_default(s, "verbosity", self.options["verbosity"])
        self.options["app_guid"] = get_or_default(s, "app_guid", self.options["app_guid"])

        if self.verbosity >= 1:
            self.p('Done Parsing.')

    def load_specfile(self, specpath):
        """
        Parse file specified by specpath and parse with json lib.
        """

        if self.verbosity >= 1:
            self.p('Opening up JSON Specfile')
        f = open(specpath,'r')
        lines = ''.join(f.readlines())
        f.close()
        self.spec = json.loads(lines)
        self.parse_spec_opts()

    def is_specfile_explicit(self):
        """
        Checks to see if the 'explicit' flag in the specfile has been set.
        """
        if not self.spec.has_key('explicit'):
            raise CommandError("JSON Specfile MUST contain an 'explicit' flag!")
        return self.spec["explicit"]

    def num_cases_in_explicit_specfile(self):
        if not self.is_specfile_explicit():
            return -1

        else:
            return len(self.spec["case"])

    def submit(self, cases):
        def pre_request(args):
            pass
        def post_request(args):
            pass

        callback_dict = {
            "pre_request": pre_request,
            "post_request": post_request,
        }
        errors = []
        fail_count = 0
        url = "%s/a/%s/receiver" % (self.host, self.domain)
        if self.app_guid:
            url = '%s/%s/' % (url, self.app_guid)
        self.stderr.write('\nURL IS: %s\nSubmitting now:\n\n' % url)
        for case in cases:
            if fail_count > 3:
                self.stderr.write(str(errors))
                self.stderr.write("Submission failed 3 times, STOPPING")
                break
            r = requests.post(url, data=self.cg.to_xform(case), allow_redirects=True, hooks=callback_dict)
            r.raise_for_status()
            if r.status_code == requests.codes.ok or r.status_code == requests.codes.created or r.status_code == requests.codes.modified:
                self.stdout.write('Submit Success: %s \n' % str(r.status_code))
            else:
                self.stdout.write('E')
                fail_count += 1
                errors.append(r)
                r.raise_for_status()

        self.stdout.write('\n')

        if len(errors):
            self.stderr.write('\n THERE WERE ERRORS:%s\n' % errors)



    def handle(self, *args, **options):
        self.options = options
        self.verbosity = int(options["verbosity"])
        if options["specfile"]:
            self.load_specfile(options["specfile"])
        try:
            NUM_CASES = args[0]
            NUM_PROPERTIES = args[1]
        except:
            self.p(self.help)
            raise CommandError("Must specify both NUM_CASES and NUM_PROPERTIES. run --help for full usage.")

        if self.spec and self.is_specfile_explicit() and self.num_cases_in_explicit_specfile() != int(NUM_CASES):
            #Yeah this is a little ridiculous, but is necessary to maintain the idea that regular command line args are always required (versus -options that are optional)
            self.p(self.help)
#            raise Exception
            raise CommandError("NUM_CASES is different from the number of cases in your spec. Your spec contains %s cases. NUM_CASES was %s Please adjust command line args. run --help for more info." % (self.num_cases_in_explicit_specfile(), NUM_CASES))

        if len(args) == 4:
            self.host = args[2]
            self.domain = args[3]
        else:
            self.host = "http://localhost:8000"
            self.domain = "test"

        self.app_guid = self.options["app_guid"]

        self.p('\nGenerating %s XForm Caseblocks!' % NUM_CASES)

        cg_args = copy.deepcopy(self.options)
        #This is so we can use keyword arguments. Following a black-list approach instead of a white-list approach to reduce likelihood of user-error (i.e. me)
        del cg_args["pythonpath"]
        del cg_args["dumppath"]
        del cg_args["traceback"]
        del cg_args["settings"]
        del cg_args["cchq_url"]
        del cg_args["specfile"] #this gets processed into memory before being passed through to CaseGenerator
        del cg_args["app_guid"]

        cg = CaseGenerator(
            NUM_CASES,
            num_properties=NUM_PROPERTIES,
            specFile=self.spec,
            **cg_args
        )
        self.cg = cg
        caseblocks = cg.generateCaseblocks()

        if options["dumppath"]:
            for case in caseblocks:
                filepath = os.path.join(self.options["dumppath"], "LT%s" % str(uuid.uuid1()).replace('-',''))
                f = open(filepath, 'w')
                f.write(self.cg.to_xform(case))
                f.close()
        else:
            self.submit(caseblocks)

        self.p('Done!')


