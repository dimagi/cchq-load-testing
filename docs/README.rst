CommCareHQ Load Tester (Case Blocks)
====================================

Purpose
-------

The purpose of this tool is to generate and send multiple case properties, in multiple forms, and submit them to the commcarehq instance of your choice.  The tool can be set to generate case data at random (the property names and values being generated at random) or to make use of a definition file (JSON) to generate a specific set of keys and values.

This tool therefore allows one to both test the ability of CCHQ to handle a large volume of submissions in a relatively short window, and it's ability to handle a large amount of cases.   The latter case (no pun intended) can then be used in conjunction with Phone Client QA  (testing whether commcare clients can handle many cases/case properties).

The tool is provided in the form of a manage.py Django command.  The initial version will require a local instance of CCHQ (don't worry you can direct this tool to submit to an instance other than the one it is being run on) as well as some other libraries laid out in the requirements.txt file (pip packages).

Installation
------------
This app should be installed in the same way as other CCHQ apps.  Make it a submodule, add it to installed apps then add in this app specific settings to the settings.py file.  An example settings.py file is provided to demonstrate all the possible settings that can be changed.  All of the settings in the example settings file will have defaults associated with them and so are all entirely optional.

Requirements
------------
Python dateutil. use ``pip install 'python-dateutil < 2.0'`` if you're running python 2.x  (dateutil 2.0 and up is for python 3.x).

Usage
-----

Generate 10 case submissions with 20 case-properties and submit it to the local CCHQ instance (via the HTTP pathway):

    ./manage.py loadtest 10 20

Generate 10 case submissions with 20 case-properties and submit it to an EXTERNAL CCHQ instance (@ a specific domain):

    ./manage.py loadtest 10 20 "http://staging.commcarehq.org" mydomain


Generate 10 case submissions with 20 case-properties based on a JSON spec:

	./manage.py loadtest 10 20 --specfile=PATH_TO_FILE

See below for details on the spec file.

Behavior:
     By default, Load Tester will generate cases and immediately submit them to the local HQ instance.  To specify a different location to submit to use --submit parameter.  To prevent submission and save the cases to disk, use --dumppath (details below).

Options:
    -v VERBOSITY, --verbosity=VERBOSITY
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=all output
    --settings=SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
    --pythonpath=PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
    --traceback           Print traceback on exception
    -s, --submit          Causes Load Tester to submit cases to the specified
                        url.
    -f SPECFILE, --specfile=SPECFILE
                        The specfile is used to indicate property names and
                        values. NUM_PROPERTIES takes precedence over this
                        file. In other words, if there are 50 properties
                        listed in the spec file but NUM_PROPERTIES is set to
                        20: Load Tester will only take the first 20 properties
                        listed in the file for case generation. If --specfile
                        is used, NUM_PROPERTIES is optional (if it is not
                        present all properties in the spec file will be used).
    -d DUMPPATH, --dumppath=DUMPPATH
                        By default all cases will be generated and submitted
                        to HQ. To prevent this behaviour and just save the
                        files to disk, use this option. FOLDER_FOR_SUBMISSIONS
                        indicates where the instances should be saved.
    --cc-version=CC_VERSION
                        Set the CC CaseXML version you would like to use.
                        Should be either "1.0" or "2.0"
    --user_id=USER_ID     Set the case user ID
    --creator_id=CREATOR_ID
                        Set the case creator ID
    --owner_id=OWNER_ID   Set the owner ID
    --case_id=CASE_ID     Set the Case ID
    --case_type=CASE_TYPE
                        Set the Case Type string
    --case_name=CASE_NAME
                        Set the Case Name string
    --device_id=DEVICE_ID
                        Set the Device ID uuid
    --external_id=EXTERNAL_ID
                        Set the External ID
    --form_xmlns=FORM_XMLNS
                        Set the XMLNS of the Form Submission
    --form_name=FORM_NAME
                        Set the "name" attribute on the instance
    --username=USERNAME   Set the submission username (different from user_id?)
    --app_guid=APP_GUID   Set the CCHQ Application GUID (for submitting cases to
                        a specific app)
    --print_xml           Print the submitted XML to console
    --version             show program's version number and exit
    -h, --help            show help message and exit



Specfile Specification
----------------------

The JSON specfile can be used in two different ways:

#) Specify case-property names to be used and the type of value each property should have (e.g 'number', 'text', 'alphanumeric', 'multiple-choice' etc).  This is the GENERALIZED specfile.

#) Specific exact case-properties and values to be used in the case submission.  No case-property values will be generated automatically.   This is the EXPLICIT specfile.

An example of a generalized specfile::

    {
        "case": {
            "mult_select_property": ["select", "foo", "bar", "baz"],
            "numbers_and_letters": ["alphanumeric"],
            "some_number": ["number", "3", false],
            "single_select_property": ["1select", "blue", "green", "red"]
        },
        "explicit": false
    }

It's also possible to include general properties that should be applied to each case (e.g. 'Case Type'). This applies to both Explicit and non-Explicit versions.::

    {
        "case": {
            "mult_select_property": ["select", "foo", "bar", "baz"],
            "numbers_and_letters": ["alphanumeric"],
            "some_number": ["number", "3", false],
            "single_select_property": ["1select", "blue", "green", "red"]
        },
        "explicit": false,
        "case_id": "LOOOL",
        "user_id": "MY_USER_GUID",
        "DEVICE_ID": "SWEET_ID",
        "form_name": "testform"
        "case_type": "My_CASE_TYPE"
    }



Note the ``"explicit"`` property is set to ``false``.  An enumeration of property value options and usage can be found later in this document.

An example of a EXPLICIT specfile::

    {
        "case": [{
            "some_property_2": 1253569,
            "some_property_3": "some_value_MCRBSXUZFGHODTPYEKJQI",
            "some_property_0": "some_value_EMYKHFIGJRQLDCWZ",
            "some_property_1": "some_value_ESHFYZUXROQLAKGJP",
            "some_property_4": 3378815
        }, {
            "some_property_13": 6175615,
            "some_property_17": "some_value_GLBADSCMERUPTHYIXZJWVKO",
            "some_property_10": "JBSAYHLWXKITQEPVOUDMCRF BRTYECWKOFVDPJS MRUVOSJAXYCPTZEHBL MVLSAOQIZT XUYFSPMLQT",
            "some_property_16": 2059006,
            "some_property_11": "IDLGVPWHCESKQAJMT OTF SYIOQTRPMVJGAKFUZ PHGKRBOWDJSZEYQMCVTFL",
            "some_property_14": 0.91117276951102621,
            "some_property_8": "GVMOQAPZLBCJHWUKEFITY KYSGCTD",
            "some_property_7": "some_value_M",
            "some_property_4": "HYVOKLIFEU UCFVWKRMTIJZXPBSDAQOEHLY FWOHQZYBXKEMRVGLACJPSDUIT",
            "some_property_5": 0.052871670500920565
        }, {
            "some_property_2": 0.67020914179633606,
            "some_property_8": "some_value_ZOAE",
            "some_property_9": "some_value_MZB",
            "some_property_18": 0.12217666932399163,
            "some_property_19": 0.80488290156366116,
            "some_property_3": "EFRUOLJPHBMKITCVG EXICYVG KV KTWBMQGHVUO VCGRFOEYBKMTULHAZSJQDWXI",
            "some_property_14": 0.70826222093529201,
            "some_property_15": 1969444,
            "some_property_16": 4646759,
            "some_property_17": 6263176,
            "some_property_10": 0.33433828214004235,
            "some_property_11": "SOIVUWGDERJBMPAHC TRIPQJGHCWKLVDB QGHVROJEDSYLAIBUCTFKMWZ CZRGYOQWLBHJXMEPKSTUF YEFV",
            "some_property_12": 0.12382389137574612,
            "some_property_13": "KGALDPJYC H JVIZBGCX KTMRPHUDIOQZCLXE QZIERTLYKFMXGPBDCJHO",
            "some_property_24": "IZDBATSVMFUGRPJCXL KZQWIGSBATMOXDRPF UZ PLDSIQABZOJMFHRWKU",
            "some_property_1": "some_value_PSWMFQYHB",
            "some_property_21": "some_value_VPEXFMDLTZCGOBWQHU",
            "some_property_20": 0.075852861258617676,
            "some_property_23": 0.64883831308172046,
            "some_property_22": 0.45205208988349577,
            "some_property_6": "ULIOYWTJRAHVPXBSDMK FVBKJM CWMYQXEFGKITRBDUALS WJPGUBOIMDLKVZCETSHFAQ",
            "some_property_7": 5241470,
            "some_property_4": 1003099,
            "some_property_5": "KWEGLFVXQRTBDCUYIHAP EQJFUGKCI BYCKVQUPFIJH ITXLFORSM UWRZM",
            "some_property_0": "TPCYDXHWIVGRLKEFBQ OJIRMXQ TFAWRG"
        }, {
            "some_property_2": 5995847,
            "some_property_0": 0.68106890921833074,
            "some_property_1": "IGRBZH"
        }],
        "explicit": true
    }

Here we see that ``"explicit"`` is set to ``true``.  This specfile will produce 3 case blocks, each with the properties and values specified in the file.


Property Value Options for Generalized Specfile
-----------------------------------------------

See the above for an example of a generalized spec file.

In the json specfile the structure would be::

    {
        "explicit": false,
        "case": {
            "SOME_PROPERTY": ["PROPERTY_TYPE", PROPERTY_OPTION_1, PROPERTY_OPTION_2, ...],
            ...
        }
    }

Here is a list of ``PROPERTY_TYPE``s and their usage (Format is ["property-type", [options]] : Description)::

    ["text", LENGTH, VARIABLE_LENGTH?] : Produces text (only with upper and lower case A-Z chars).  LENGTH sets the length the value should be.  if VARIABLE_LENGTH? is set to True, the value generated will vary in length between 1 and LENGTH (inclusive).  LENGTH and VARIABLE_LENGTH? are both optional (but you cannot specify VARIABLE_LENGTH? without specifying LENGTH!).  LENGTH defaults to 10.  VARIABLE_LENGTH? defaults to True.
    
    ["alphanumeric", LENGTH, VARIABLE_LENGTH?] : Same as above except with the additional numerical chars.
    
    ["number", LENGTH, VARIABLE_LENGTH?] : As above, but only with numbers (integers).

    ["double"] : As a random double.
    
    ["select1", OPTION_LIST] : if OPTION_LIST is not specified: randomly generates a set of options. OPTION_LIST is an list of text values: e.g. "foo", "bar", "bash".

    ["select", OPTION_LISTS] : As above, but selects between 1 and number_of_items_in_list items (as with a multi-select question).  Result is ' ' seperated string of options.

    ["date", START_DATE, END_DATE] : generates a date between the two range points (inclusive).

    ["datetime", START_DATETIME, END_DATETIME] : As above, but with datetimes.