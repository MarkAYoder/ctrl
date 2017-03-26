import warnings
import socketserver
import platform
import getopt, sys, signal
import importlib
import threading
import time

# from hanging_threads import start_monitoring
# monitoring_thread = start_monitoring()

import ctrl.server

def one_line_warning(message, category, filename, lineno, line=None):
    return " {}:{}: {}:{}\n".format(filename, lineno, category.__name__, message)

def brief_warning(message, category, filename, lineno, line=None):
    return "*{}\n".format(message)

def usage():
    print('Controller Server (version {})'.format(ctrl.server.version()))
    print("""usage: python server [option] ...
Options are:
-c     : skip simulated controller calibration
-C arg : controller class             (default 'Controller')
-h     : print this help message and exit
-H arg : set hostname                 (default 'localhost')
-l arg : set log size in seconds      (default 120s)
-m arg : controller module            (default 'ctrl.bbb')
-p arg : set port                     (default 9999)
-t arg : set sampling rate in second  (default 0.01s)
-v arg : set verbose level            (default 1)""")

def main():

    # Parse command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cC:fhH:l:m:p:t:v:", ["help"])

    except getopt.GetoptError as err:
        # print help information and exit:
        print('server: illegal option {}'.format(sys.argv[1:]))
        usage()
        sys.exit(2)

    # Sampling period and log size (s)
    Ts, log_size = 0.01, 120

    # HOST AND PORT
    HOST, PORT = "localhost", 9999

    # verbose_level
    verbose_level = 1

    # calibrate
    calibrate = 1

    # default module
    module = 'ctrl'
    ctrl_class = 'Controller'

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "-H":
            HOST = a
        elif o in "-l":
            log_size = float(a)
        elif o in "-p":
            PORT = int(a)
        elif o in "-t":
            Ts = float(a)
        elif o in "-v":
            verbose_level = int(a)
        elif o == "-c":
            calibrate = 0
        elif o == "-m":
            module = a
        elif o == "-C":
            ctrl_class = a
        else:
            assert False, "Unhandled option"

    # Modify warnings
    if verbose_level > 2:
        pass # standard formating
    elif verbose_level > 1:
        # one liner
        warnings.formatwarning = one_line_warning
    else:
        # brief
        warnings.formatwarning = brief_warning

    # Create controller
    obj_class = getattr(importlib.import_module(module),
                        ctrl_class)
    controller = obj_class()
    controller.set_period(Ts)
    controller.reset()
    ctrl.server.set_controller(controller)
    ctrl.server.verbose(verbose_level)

    # Start server

    # Create the server, binding to HOST and PORT
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), 
                                    ctrl.server.Handler)
    
    # Initiate server

    print('Controller Server (version {})'.format(ctrl.server.version()))
    if verbose_level > 0:
        print('> Options:')
        print('    Hostname[port]: {}[{}]'.format(HOST, PORT))
        print('    Sampling rate : {}s'.format(controller.get_period()))
        print('    Log size      : {}s'.format(log_size))
        print('    Verbose level : {}'.format(verbose_level))
        print(controller.info('all'))
        print('> Server started...')
        
    # run server in a separate thread
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

    try:

        print("> Hit Ctrl-C or Use 'python kill_server.py' to exit server")
        
        # Wait forever
        thread.join()

    except KeyboardInterrupt:
        # Catch Ctrl-C
        pass
            
    finally:

        # shutdown server
        controller.stop()
        server.shutdown()
        thread.join()
            
        # say bye
        print("\nBye Beaglebone!")

if __name__ == "__main__":
    main()