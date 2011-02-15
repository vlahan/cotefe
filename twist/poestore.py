#
# Copyright (c) 2007, Technische Universitaet Berlin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - Neither the name of the Technische Universitaet Berlin nor the names
#   of its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Vlado Handziski (handzisk at tkn.tu-berlin.de)

import os

import ConfigParser

from twisted.internet import defer
from twisted.python import log, util as tutil

from pysnmp.entity import engine, config
from pysnmp.carrier.twisted import dispatch
from pysnmp.carrier.twisted.dgram import udp
from pysnmp.entity.rfc3413.twisted import cmdgen
from pysnmp.proto import rfc1902

config_parser=ConfigParser.SafeConfigParser()

config_parser.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

poe_hosts = config_parser.get('poe','hosts')
poe_forwarding_ports = config_parser.get('poe','forwarding_ports')
poe_username = config_parser.get('poe','username')
poe_auth_password = config_parser.get('poe', 'auth_password')
poe_priv_password = config_parser.get('poe', 'priv_password')
poe_mac_table_oid = rfc1902.ObjectName(config_parser.get('poe', 'mac_table_oid'))
poe_port_table_oid = rfc1902.ObjectName(config_parser.get('poe', 'port_table_oid'))
poe_port_status_table_oid = rfc1902.ObjectName(config_parser.get('poe', 'port_status_table_oid'))
poe_port_power_control_oid=rfc1902.ObjectName(config_parser.get('poe', 'port_power_control_oid'))

class TwistPoeStore(object):

    def __init__(self):
        self.mac_to_host_port={}
        self.host_port_to_mac={}
        self.mac_status={}
        self.poe_hosts=[host.strip() for host in poe_hosts.strip().split(",")]
        self.poe_forwarding_ports=[port.strip() for port in poe_forwarding_ports.strip().split(",")]
        self.snmpEngine = engine.SnmpEngine()
        self.snmpEngine.registerTransportDispatcher(dispatch.TwistedDispatcher())
        config.addV3User(self.snmpEngine, poe_username,
                         config.usmHMACSHAAuthProtocol, poe_auth_password,
                         config.usmDESPrivProtocol, poe_priv_password)
        config.addTargetParams(self.snmpEngine, 'poe_params', poe_username, 'authPriv')
        for host in self.poe_hosts:
            config.addTargetAddr(self.snmpEngine, 'poe_host_%s' % host,
                                 config.snmpUDPDomain,
                                 (host, 161), 'poe_params')

        config.addSocketTransport(self.snmpEngine, udp.domainName,
                                  udp.UdpTwistedTransport().openClientMode())

        self.bulkCmdGen = cmdgen.BulkCommandGenerator()
        self.setCmdGen = cmdgen.SetCommandGenerator()

    def snmp_tableget(self, host, parent_oid, oid=None, table=None):
        if oid is None:
            oid=parent_oid
        df = self.bulkCmdGen.sendReq(self.snmpEngine, 'poe_host_%s' % host, 0, 25, ((oid, None),))
        df.addCallback(self._cb_snmp_tableget, host, parent_oid, table)
        return df

    def _cb_snmp_tableget(self, (errorIndication, errorStatus, errorIndex, varBindTable), host, parent_oid, table=None):
        if errorIndication or errorStatus:
            log.err('Poe Store Error: %s %s %s' % (errorIndication, errorStatus.prettyPrint(), errorIndex))
        else:
            if table is None:
                table=[]
            table=table + [varBindRow for varBindRow in varBindTable if parent_oid.isPrefixOf(varBindRow[0][0])]
            if parent_oid.isPrefixOf(varBindTable[-1][0][0]):
                oid=varBindTable[-1][0][0]
                return self.snmp_tableget(host, parent_oid, oid, table)
            else:
                return table

    def snmp_set(self, host, oid, value):
        df = self.setCmdGen.sendReq(self.snmpEngine, 'poe_host_%s' % host, ((oid, value),))
        df.addCallback(self._cb_snmp_set)
        return df

    def _cb_snmp_set(self, (errorIndication, errorStatus, errorIndex, varBindTable)):
        if errorIndication or errorStatus:
           log.err('Poe Store Error: %s %s %s' % (errorIndication, errorStatus.prettyPrint(), errorIndex))
        else:
           return varBindTable

    def update_mapping(self):
        self.mac_to_host_port={}
        self.host_port_to_mac={}
        l=[]
        for host in self.poe_hosts:
            d1=self.snmp_tableget(host, poe_mac_table_oid)
            d2=self.snmp_tableget(host, poe_port_table_oid)
            dhl=defer.DeferredList([d1,d2], fireOnOneErrback=False, consumeErrors=True)
            dhl.addCallback(self._cb_process_mac_host_port_tables, host)
            l.append(dhl)
        dl=defer.DeferredList(l, fireOnOneErrback=False, consumeErrors=True)
        return dl

    def _cb_process_mac_host_port_tables(self, tables, host):
        mac_dict={}
        mac_oid_prefix_string=poe_mac_table_oid.prettyPrint()+'.'
        port_oid_prefix_string=poe_port_table_oid.prettyPrint()+'.'
        for varBindRow in tables[0][1]:
            [(oid, mac)] = varBindRow
            mac_string=':'.join( ['%02X' % ord( x ) for x in mac.prettyPrint() ] ).strip()
            mac_string=mac_string.lower()
            oid_string=oid.prettyPrint().replace(mac_oid_prefix_string,'')
            mac_dict[oid_string]=mac_string
        for varBindRow in tables[1][1]:
            [(oid, port)] = varBindRow
            oid_string=oid.prettyPrint().replace(port_oid_prefix_string,'')
            port_string=port.prettyPrint()
            try:
                mac_string=mac_dict[oid_string]
                if port_string not in self.poe_forwarding_ports:
                    self.mac_to_host_port[mac_string]=(host, port_string)
                    self.host_port_to_mac[(host, port_string)]=mac_string
            except KeyError:
                pass

    def _cb_process_host_port_status_table(self, table, host):
        oid_prefix_string=poe_port_status_table_oid.prettyPrint()+'.'
        for row in table:
            [(oid, status)]=row
            port=oid.prettyPrint().replace(oid_prefix_string,'')
            try:
                if status==rfc1902.Integer(1):
                    value='link_up'
                elif status==rfc1902.Integer(2):
                    value='link_down'
                else:
                    value='unknown'
                self.mac_status[self.host_port_to_mac[(host,port)]]=value
            except KeyError:
                pass

    def get_mac_status_dict(self, r=None):
        l=[]
        for host in self.poe_hosts:
            hl=[]
            d=self.snmp_tableget(host, poe_port_status_table_oid)
            d.addCallback(self._cb_process_host_port_status_table, host)
            hl.append(d)
            dhl=defer.DeferredList(hl, fireOnOneErrback=False, consumeErrors=True)
            l.append(dhl)
        dl=defer.DeferredList(l, fireOnOneErrback=False, consumeErrors=True)
        dl.addCallbacks(self._cb_get_mac_status_dict, self._eb_poestore)
        return dl

    def _cb_get_mac_status_dict(self, r=None):
        return self.mac_status

    def get_supernode_status(self, cached=True):
        if cached and self.mac_to_host_port and self.host_port_to_mac:
            return self.get_mac_status_dict()
        else:
            d=self.update_mapping()
            d.addCallback(self.get_mac_status_dict)
            return d
 
    def control_supernode_power(self, mac_list, action):
        l=[]
        if action=='enable':
            value=rfc1902.Integer(2)
        else:
            value=rfc1902.Integer(3)
        for mac_string in mac_list:
            try:
                host, port = self.mac_to_host_port[mac_string]
                oid=rfc1902.ObjectName('.'.join([poe_port_power_control_oid.prettyPrint(), str(port)]))
                l.append(self.snmp_set(host, oid, value))
            except KeyError:
                continue
        dl=defer.DeferredList(l, fireOnOneErrback=False, consumeErrors=True)
        dl.addCallback(self._cb_log, action)
        return dl           

    def _cb_log(self, notification, action):
        results=[result for (success, result) in notification if success==True]
        log.msg('PoE Store Action: Succesful action "%s" on %d supernodes' % (action, len(results)))
  
    def _eb_poestore(self, f):
        log.err('PoE Store Error: %s' % f.getErrorMessage().strip())
        raise f
