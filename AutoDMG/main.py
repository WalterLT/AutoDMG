#-*- coding: utf-8 -*-
#
#  main.py
#  AutoDMG
#
#  Created by Per Olofsson on 2013-09-19.
#  Copyright Per Olofsson, University of Gothenburg 2013. All rights reserved.
#

import sys
import argparse

#import modules required by application
import objc
import Foundation

objc.setVerbose(1)

from IEDLog import LogDebug, LogInfo, LogNotice, LogWarning, LogError, LogMessage
from IEDUtil import *
import platform


#def addargs_updates(argparser):
#    sp = argparser.add_subparsers()
#    pullparser = sp.add_parser(u"pull", help=doupdates_pull.__doc__)
#    pullparser.set_defaults(func=doupdates_pull)
#    showparser = sp.add_parser(u"show", help=doupdates_show.__doc__)
#    showparser.add_argument(u"build", help=u"OS build number")
#    showparser.set_defaults(func=doupdates_show)
#    downloadparser = sp.add_parser(u"download", help=doupdates_download.__doc__)
#    downloadparser.add_argument(u"build", help=u"OS build number")
#    downloadparser.set_defaults(func=doupdates_download)


def gui_main():
    import AppKit
    from PyObjCTools import AppHelper
    
    # import modules containing classes required to start application and load MainMenu.nib
    import IEDAppDelegate
    import IEDController
    import IEDSourceSelector
    import IEDAddPkgController
    import IEDAppVersionController
    
    # pass control to AppKit
    AppHelper.runEventLoop()
    
    return 0


def cli_main(argv):
    from IEDCLIController import IEDCLIController
    clicontroller = IEDCLIController.alloc().init()
    
    logFile = None
    
    try:
        # Initialize user defaults before application starts.
        defaultsPath = NSBundle.mainBundle().pathForResource_ofType_(u"Defaults", u"plist")
        defaultsDict = NSDictionary.dictionaryWithContentsOfFile_(defaultsPath)
        defaults.registerDefaults_(defaultsDict)
        
        p = argparse.ArgumentParser()
        p.add_argument(u"-v", u"--verbose", action=u"store_true", help=u"Verbose output")
        p.add_argument(u"-l", u"--logfile", help=u"Log to file")
        sp = p.add_subparsers(title=u"subcommands", dest=u"subcommand")
        
        # Populate subparser for each verb.
        for verb in clicontroller.listVerbs():
            verb_method = getattr(clicontroller, u"cmd%s_" % verb.capitalize())
            addargs_method = getattr(clicontroller, u"addargs%s_" % verb.capitalize())
            parser = sp.add_parser(verb, help=verb_method.__doc__)
            addargs_method(parser)
            parser.set_defaults(func=verb_method)
        
        args = p.parse_args(argv)
        #if args.verbose:
        #    pass
        
        if args.logfile:
            if args.logfile == u"-":
                # default is StdErr.
                pass
            else:
                try:
                    logFile = open(args.logfile, u"a", buffering=1)
                except OSError as e:
                    print >>sys.stderr, (u"Couldn't open %s for writing" % (args.logfile)).encode(u"utf-8")
                    return 1
                LogToFile(logFile)
        
        # Log version info on startup.
        version, build = IEDUtil.getAppVersion()
        LogNotice(u"AutoDMG v%@ build %@", version, build)
        name, version, build = IEDUtil.readSystemVersion_(u"/")
        LogNotice(u"%@ %@ %@", name, version, build)
        LogNotice(u"%@ %@ (%@)", platform.python_implementation(),
                                 platform.python_version(),
                                 platform.python_compiler())
        LogNotice(u"PyObjC %@", objc.__version__)
        
        return args.func(args)
        #from PyObjCTools import AppHelper
        #AppHelper.runConsoleEventLoop(installInterrupt=True)
    finally:
        clicontroller.cleanup()


# Decode arguments as utf-8 and filter out arguments from Finder and
# Xcode.
decoded_argv = list()
i = 1
while i < len(sys.argv):
    arg = sys.argv[i].decode(u"utf-8")
    if arg.startswith(u"-psn"):
        pass
    elif arg == u"-NSDocumentRevisionsDebugMode":
        i += 1
    elif arg.startswith(u"-NS"):
        pass
    else:
        decoded_argv.append(arg)
    i += 1

# If no arguments are supplied, assume the GUI should be started.
if len(decoded_argv) == 0:
    sys.exit(gui_main())
# Otherwise parse the command line arguments.
else:
    sys.exit(cli_main(decoded_argv))
