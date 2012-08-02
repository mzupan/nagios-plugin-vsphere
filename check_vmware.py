#!/usr/bin/env python

import sys
import optparse
import time

try:
    from pysphere import *
except ImportError, e:
    print e
    sys.exit(2)

def main(argv):
    p = optparse.OptionParser(conflict_handler="resolve", description= "This Nagios plugin checks the health of vmware hosts.")

    p.add_option('-H', '--host', action='store', type='string', dest='host', default='127.0.0.1', help='The hostname you want to connect to')
    p.add_option('-u', '--user', action='store', type='string', dest='user', default=None, help='The username you want to login as')
    p.add_option('-p', '--pass', action='store', type='string', dest='passwd', default=None, help='The password you want to use for that user')
    p.add_option('-A', '--action', action='store', type='choice', dest='action', default='connect', help='The action you want to take',
                 choices=['connect', 'general_health'])
    p.add_option('-W', '--warning', action='store', dest='warning', default=None, help='The warning threshold we want to set')
    p.add_option('-C', '--critical', action='store', dest='critical', default=None, help='The critical threshold we want to set')
    options, arguments = p.parse_args()

    host = options.host
    user = options.user
    passwd = options.passwd
    action = options.action
    warning = float(options.warning or 0) 
    critical = float(options.critical or 0) 

    if user is None:
        print "You need to enter a username"
        sys.exit(2)
    if passwd is None:
        print "You need to enter a password"
        sys.exit(2)

    #
    # always make the connection first
    server = VIServer()
    start = time.time()
    try:
        server.connect(host, user, passwd)
    except Exception, e:
        print "Connection to VSphere failed: ", e
        sys.exit(2)
    conn_time = time.time() - start
    conn_time = round(conn_time, 0)

    if action == "general_health":
        return general_health(server, warning, critical)
    else:
        return check_connect(conn_time, warning, critical)


def performance_data(params):
    data= " |"
    for p in params:
        p += (None,None,None,None)
        param,param_name,warning,critical = p[0:4];
        data +=" %s=%s" % (param_name,str(param))    
        if warning or critical:
            warning = warning or 0
            critical = critical or 0
            data += ";%s;%s" % (warning,critical)
    return data

def numeric_type(param):
    if ((type(param) == float or type(param) == int or param == None)):
        return True
    return False

def check_levels(param, warning, critical,message,ok=[]):
    if (numeric_type(critical) and numeric_type(warning)):
        if param >= critical:
            print "CRITICAL - " + message
            return 2
        elif param >= warning:
            print "WARNING - " + message
            return 1
        else:
            print "OK - " + message
            return 0
    else:
        if param in critical:
            print "CRITICAL - " + message
            return 2

        if param in warning:
            print "WARNING - " + message
            return 1

        if param in ok:
            print "OK - " + message
            return 0

        # unexpected param value
        print "CRITICAL - Unexpected value : %d" % param + "; " + message
        return 2


def check_connect(conn_time, warning, critical):
    warning = warning or 3
    critical = critical or 6
    message = "Connection took %i seconds" % conn_time
    message += performance_data([(conn_time,"connection_time",warning,critical)])

    return check_levels(conn_time,warning,critical,message)

def general_health(server, warning, critical):
    pm = server.get_performance_manager()

    props = server._retrieve_properties_traversal(property_names=['name', 'summary.overallStatus'], obj_type="HostSystem")

    
    errors = []
    for prop_set in props:
        for prop in prop_set.PropSet:
            if prop.Name == "name":
                host = prop.Val
            elif prop.Name == "summary.overallStatus":
                if prop.Val != "green":
                    errors.append("Host: %s is in state of %s" % (host, prop.Val))

    if len(errors) == 0:
        print "All hosts are green"
        sys.exit(0)
    else:
        for error in errors:
            print error

        sys.exit(2)
#
# main app
#
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
