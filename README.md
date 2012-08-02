# Nagios-Vsphere

## Overview

This is a simple Nagios check script to monitor your VMware Vsphere cluster(s). 

## Authors

### Main Author
 Mike Zupan mike -(at)- zcentric.com

## Installation

In your Nagios plugins directory run

<pre><code>git clone git://github.com/mzupan/nagios-plugin-vsphere.git</code></pre>

Then make sure you have the needed vsphere python module

<pre><code>pip install -U pysphere</code></pre>

or

<pre><code>easy_install -U pysphere</code></pre>

## Usage

### Install in Nagios

Edit your commands.cfg and add the following

<pre><code>
define command {
    command_name    check_vsphere
    command_line    $USER1$/nagios-plugin-vsphere/check_vsphere.py -H $HOSTADDRESS$ -A $ARG1$ -u $ARG2$ -p $ARG3$ -W $ARG4$ -C $ARG5$ 
}
</code></pre>

Then you can reference it like the following. This is is my services.cfg

#### Check Connection

This will check the host that is listed for how long it takes to connect. It will issue a warning if the connection to the server takes 2 seconds and a critical error if it takes over 4 seconds

<pre><code>
define service {
    use                 	generic-service
    host_name          		vsphere01
    service_description     Vsphere Connect Check
    check_command           check_vsphere!connect!username!passwd!2!4
}
</code></pre>

#### Check General Health

This will check the health state of your vsphere cluster. It will alert a critical error if vsphere is showing an alert for a host

<pre><code>
define service {
    use                 	generic-service
    host_name          		vsphere01
    service_description     Vsphere Health Check
    check_command           check_vsphere!general_health!username!passwd!0!0
}
</code></pre>

