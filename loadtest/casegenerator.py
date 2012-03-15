import json
from propertygenerartors import PropertyValueGenerator as pvg
from casexml.apps.case.tests.util import CaseBlock
import datetime

def generate_user_id():
    return "LOAD_TESTING_USER_%s" % str(datetime.datetime.now().strftime('%d%m%Y_%H%M'))

def generate_case_id():
    return "LOAD_TESTING_CASE_%s" % str(datetime.datetime.now().strftime('%d%m%Y_%H%M'))


class GeneratorFromSpec():
    is_explicit = False

    def __init__(self,specFile,num_cases,case_id=None,creator_id=None,owner_id=None,case_type=None,case_name=None,cc_version="1.0",external_id=None):
        """
        Assumes specFile is already converted into a python object (from JSON)
        <!-- user_id (==creator_id) - At Most One: the GUID of the user responsible for this case creation -->
        <!-- case_id - Exactly One: The id of the abstract case to be modified (even in the case of creation) -->
        <case_type/>             <!-- At Most One: Modifies the Case Type for the case -->
        <case_name/>                <!-- At Most One: A semantically meaningless but human  readable name associated with the case -->
        <date_opened/>              <!-- At Most One: Modifies the Date the case was opened -->
        <owner_id/>                 <!-- At Most One: Modifies the owner of this case -->
        """
        self.is_explicit = self.specfile["explicit"]
        self.props_funcs = {}  #used if explicit = False
        self.cases = []  #used if explicit = True
        self.num_cases = num_cases

        self.case_type = "LOAD_TESTING_CASE" if not case_type else case_type
        self.case_name = "LOAD_TESTING_CASE_NAME" if not case_name else case_name
        self.case_id = generate_case_id() if not case_id else case_id
        self.creator_id = generate_user_id() if not creator_id else creator_id
        self.specfile = specFile
        self.owner_id = owner_id
        self.creator_id = creator_id
        self.external_id = external_id
        self.cc_version = cc_version

    def generateCaseblocks(self):
        """
        Generates caseblocks based on the specfile
        """
        if not self.props_funcs and not self.cases:
            self._make_props()
        retcases = []
        for i in range(self.num_cases):
            create = True if i == 0 else False
            update = self.cases[i] if self.is_explicit else self.get_fresh_propdict()
            block = CaseBlock(
                create=create,
                case_id=self.case_id,
                user_id=self.creator_id,
                owner_id=self.creator_id,
                case_type=self.case_type,
                version=self.cc_version,
                update=update
            )
            retcases.append(block)
        return retcases

    def _make_props(self):
        self._make_props_explicit() if self.is_explicit else self._make_props_general()

    def _make_props_explicit(self):
        for case in self.specfile["case"]:
            c = {}
            for key, value in case.items():
                c[key] = value
            self.cases.append(c)

    def _make_props_general(self):
        for key, value in self.specfile["case"].items():
            self.props_funcs[key] = pvg(value.pop(0),value)

    def get_fresh_propdict(self):
        ret_dict = {}
        for key, value in self.props_funcs:
            ret_dict[key] = value()
        return ret_dict
