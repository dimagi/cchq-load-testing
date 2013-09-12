from casexml.apps.case.mock import CaseBlock
from propertygenerartors import PropertyValueGenerator as pvg
from specmaker import getspec, _rand_chars, NUMBERS
from datetime import date, timedelta
from xml.etree import ElementTree
import datetime
import random
import uuid
import pprint
import json

HTML_BOILERPLATE = """<?xml version='1.0'?><data uiVersion="1" version="19" name="%(form_name)s" xmlns:jrm="http://dev.commcarehq.org/jr/xforms" xmlns="%(form_xmlns)s">%(case)s<meta><deviceID>%(deviceid)s</deviceID><timeStart>%(timestart)s</timeStart><timeEnd>%(timeend)s</timeEnd><username>%(username)s</username><userID>%(userid)s</userID><instanceID>%(instanceid)s</instanceID></meta></data>"""

def generate_user_id():
    return "LOAD_TESTING_USER_%s" % str(datetime.datetime.now().strftime('%d%m%Y_%H%M'))

def generate_case_id():
    return "LOAD_TESTING_CASE_%s" % str(datetime.datetime.now().strftime('%d%m%Y_%H%M'))

def generate_device_id():
    return "LOAD_TESTING_DEVICE_ID_%s" % _rand_chars(NUMBERS,3)

class CaseGenerator():
    """
    >>> cg = CaseGenerator(2)
    >>> cg.generateCaseblocks()
    """
    is_explicit = False

    def __getitem__(self, item):
        return getattr(self, item)

    def __init__(self,
                 num_cases,
                 num_properties=None,
                 specFile=None,
                 case_id=None,
                 device_id=None,
                 creator_id=None,
                 owner_id=None,
                 user_id=None,
                 username=None,
                 case_type=None,
                 case_name=None,
                 cc_version="1.0",
                 external_id=None,
                 form_xmlns="http://www.commcarehq.org/example/hello-world",
                 form_name="LOAD_TEST_FORM",
                 verbosity=1):
        """
        Assumes specFile is already converted into a python object (from JSON)
        <!-- user_id (==creator_id) - At Most One: the GUID of the user responsible for this case creation -->
        <!-- case_id - Exactly One: The id of the abstract case to be modified (even in the case of creation) -->
        <case_type/>             <!-- At Most One: Modifies the Case Type for the case -->
        <case_name/>                <!-- At Most One: A semantically meaningless but human  readable name associated with the case -->
        <date_opened/>              <!-- At Most One: Modifies the Date the case was opened -->
        <owner_id/>                 <!-- At Most One: Modifies the owner of this case -->
        """
        self.num_properties = int(num_properties)
        self.has_user_specfile = specFile is not None
        self.specfile = specFile if specFile else getspec(self.num_properties)
        self.props_funcs = {}  #used if explicit = False
        self.cases = []  #used if explicit = True
        self.num_cases = int(num_cases)


        self.case_type = "LOAD_TESTING_CASE" if not case_type else case_type
        self.case_name = "LOAD_TESTING_CASE_NAME" if not case_name else case_name
        self.case_id = generate_case_id() if not case_id else case_id
        self.creator_id = generate_user_id() if not creator_id else creator_id
        self.owner_id = generate_user_id() if not owner_id else owner_id
        self.username = username if username else "LOAD_TESTER_CCUSER"
        self.user_id = generate_user_id() if not user_id else user_id
        self.external_id = external_id or 'LOAD_TESTER_EXTERNAL_ID'
        self.device_id = device_id if device_id else generate_device_id()
        self.cc_version = cc_version
        self.is_explicit = self.specfile["explicit"]
        self.form_xmlns = form_xmlns
        self.form_name = form_name
        self.verbosity = int(verbosity)

        if self.verbosity > 1:
            print 'Succesfully created CaseGenerator'
            print "CaseGenerator Options:\n" \
                    "\tNumber of Cases:%(num_cases)s\n" \
                    "\tNumber of Properties per case: %(num_properties)s\n" \
                    "\tHas user generated specfile?: %(has_user_specfile)s\n" \
                    "\tIs spec explicit?: %(is_explicit)s\n" \
                    "\tCaseBlock Version: %(cc_version)s\n" \
                    "\tOwner_id: %(owner_id)s\n" \
                    "\tCreator_id: %(creator_id)s\n" \
                    "\tExternal_id: %(external_id)s\n" \
                    "\tDevice_id: %(device_id)s\n" \
                    "\tCase Type: %(case_type)s\n" \
                    "\tCase Name: %(case_name)s\n" \
                    "\tCase ID: %(case_id)s\n" % self

            print "SPEC:"
            pprint.pprint(self.specfile, indent=2)
            print "SPEC IN JSON"
            print "\n"
            print json.dumps(self.specfile)
            print "\n"

    def to_xform(self, case):
        """
        Throws the caseblock into some wrapper xml, converting it to a submissionable xform instance
        """

        #HTML_BOILERPLATE requires case,deviceid,timestart,timeend,username,userid,instanceid
        #times need to be isoformatted.
        if self.verbosity > 0:
            print 'Generating XML for Case.'
        dict = {}
        dict["case"] = ElementTree.tostring((case.as_xml()))
        dict["deviceid"] = self.device_id
        dict["timestart"] = (datetime.datetime.now() - timedelta(seconds=2)).isoformat()
        dict["timeend"] = datetime.datetime.now().isoformat()
        dict["username"] = self.username
        dict["userid"] = self.creator_id if not self.user_id else self.user_id
        dict["instanceid"] = "LT%s" % str(uuid.uuid1()).replace('-','')
        dict["form_xmlns"] = self.form_xmlns
        dict["form_name"] = self.form_name

        return HTML_BOILERPLATE % dict

    def generateCaseblocks(self):
        """
        Generates caseblocks based on the specfile
        """
        if not self.props_funcs and not self.cases:
            self._make_props()
        retcases = []
        for i in range(self.num_cases):
            date_opened = None
            create = True if i == 0 else False
            if create:
                date_opened = datetime.datetime.now()
            update = self.cases[i] if self.is_explicit else self.get_fresh_propdict()

            d = dict(
                create=create,
                date_opened=date_opened,
                case_id=self.case_id,
                user_id=self.user_id,
                owner_id=self.owner_id,
                case_type=self.case_type,
                version=self.cc_version,
                external_id=self.external_id,
                update=update,
                date_modified=datetime.datetime.now(),
                case_name=self.case_name,
            )

            ##### CONSOLE OUTPUT ########################################
            if self.verbosity > 1:
                print '\nActually generating a case:'
                print 'Create?: %s' % create
                print 'Case_ID: %(case_id)s\n'\
                        'Creator_id: %(creator_id)s\n' \
                        'Owner_id: %(creator_id)s\n' \
                        'Case_type: %(case_type)s\n' \
                        'Version: %(cc_version)s\n' % self
                print 'Update args: %s\n' % update
            elif self.verbosity == 1:
                print 'Generating Case.'
            if self.verbosity == 2:
                print 'Whole Dict %s' % d
            ############################################################
            if date_opened:
                block = CaseBlock(**d)
            else:
                del d["date_opened"]
                block = CaseBlock(**d)
            retcases.append(block)
        return retcases

    def _make_props(self):
        self._make_props_explicit() if self.is_explicit else self._make_props_general()

    def _make_props_explicit(self):
        for case in self.specfile["case"]:
            c = {}
            for key, value in case.items():
                if not isinstance(value,str) and not isinstance(value, unicode):
                    cleaned = str(value)
                else:
                    cleaned = value
                c[key] = cleaned
            self.cases.append(c)

    def _make_props_general(self):
        for key, value in self.specfile["case"].items():
            pvg_func = value.pop(0)
            pvg_arg = tuple(value)
            self.props_funcs[key] = pvg(pvg_func, *pvg_arg)

    def get_fresh_propdict(self):
        ret_dict = {}
        for key, value in self.props_funcs.items():
            ret_dict[key] = value.getValue()
        return ret_dict
