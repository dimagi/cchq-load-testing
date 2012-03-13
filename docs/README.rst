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

Usage
-----

Generate 10 case submissions with 20 case-properties each:

    ./manage.py loadtest 10 20

Generate 10 case submissions with 20 case-properties and submit it to the local CCHQ instance (via the HTTP pathway):

    ./manage.py loadtest 10 20 submit

Generate 10 case submissions with 20 case-properties and submit it to an EXTERNAL CCHQ instance (via the HTTP pathway):

    ./manage.py loadtest 10 20 submit [URL_TO_CCHQ]


Generate 10 case submissions with 20 case-properties based on a JSON spec:

	./manage.py loadtest 10 20 submit [URL_TO_CCHQ] --specfile=PATH_TO_FILE 


Full Usage (all options in brackets are... optional):

	./manage.py loadtest NUM_CASES NUM_PROPERTIES [submit [URL_TO_CCHQ]] [--specfile=PATH_TO_FILE] [--dumppath=FOLDER_FOR_SUBMISSIONS] [--quiet]


Options:
     submit [URL_TO_CCHQ]:
     	Presence of this keyword causes Load Tester to submit the generated Cases to CCHQ. When URL_TO_CCHQ is used, the submission will be sent to that URL, as opposed to the local hq instance.  Both types of submission will occur via HTTP/S.

     --specfile=PATH_TO_FILE:
        The specfile is used to indicate property names and values. NUM_PROPERTIES takes precedence over this file.  In other words, if there are 50 properties listed in the spec file but NUM_PROPERTIES is set to 20: Load Tester will only take the first 20 properties listed in the file for case generation.   If --specfile is used, NUM_PROPERTIES is optional (if it is not present all properties in the spec file will be used).

     --dumppath=FOLDER_FOR_SUBMISSIONS:
        By default, the generated cases will be output to inidividual files in the same location as manage.py.  Use FOLDER_FOR_SUBMISSIONS to indicate an alternative location for generated cases.

     --quiet:
        Not interested in a play-by-play?  Use this to simply get a summary note at the end of the run.
