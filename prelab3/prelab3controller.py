# preLab3 controller Skeleton
#
# Based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import *
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time

log = core.getLogger()

class Firewall (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_firewall (self, packet, packet_in):
    # The code in here will be executed for every packet.
    print "Example Code."
    src = packet.find('ipv4')
    src_ip = src.src_ip
    dest = packet.find('ipv4')
    dest_ip = dest.dest_ip

    if packet.find('ARP') is not None:
      self.accept_packet(self,packet,packet_in)
    elif packet.find('ICMP') is not None:
      self.accept_packet(self,packet,packet_in)
    elif packet.find('TCP') and is_workstation(src_ip) and is_workstation(dest_ip):
      self.accept_packet(self,packet,packet_in)
    elif packet.find('TCP') and is_ITworkstation(src_ip) and is_Laptop(dest_ip):
      self.accept_packet(self,packet,packet_in)
    elif packet.find('TCP') and is_Laptop(src_ip) and is_ITworkstation(dest_ip):
      self.accept_packet(self,packet,packet_in)
    elif packet.find('TCP') and is_Laptop(src_ip) and is_Server2(dest_ip):
      self.accept_packet(self,packet,packet_in)
    elif packet.find('TCP') and is_Server2(src_ip) and is_Laptop(dest_ip):
      self.accept_packet(self,packet,packet_in)
    elif packet.find('UDP') and (is_ITworkstation(src_ip) or is_Laptop(src_ip)) and is_DNSserver(dest_ip):
      self.accept_packet(self,packet,packet_in)
    elif packet.find('UDP') and (is_ITworkstation(dest_ip) or is_Laptop(dest_ip)) and is_DNSserver(src_ip):
      self.accept_packet(self,packet,packet_in)
    else :
      drop_packet(self,packet,packet_in)


    def accept_packet(self,packet,packet_in):
      msg = of.ofp_packet_out()
      msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      msg.data = packet_in
      msg.in_port = event.port
      self.connection.send(msg)
    
    def drop_packet (self,packet,packet_in):
      msg = of.ofp_packet_out()
      msg.buffer_id = event.ofp.buffer_id
      msg.in_port = event.port
      self.connection.send(msg)

    def is_workstation(ip):
      if (ip=='200.20.2.4' || ip=='200.20.2.5' || ip=='200.20.2.6' || ip=='200.20.2.7'):
        return True
      else:
        return False

    def is_ITworkstation(ip):
      if (ip=='200.20.2.6' || ip=='200.20.2.7'):
        return True
      else:
        return False
    
    def is_Laptop(ip):
      if (ip=='200.20.2.8' || ip=='200.20.2.9'):
        return True
      else:
        return False
    
    def is_Server2(ip):
      if (ip=='200.20.2.1'):
        return True
      else:
        return False
    
    def is_DNSserver(ip):
      if (ip=='200.20.2.3'):
        return True
      else:
        return False

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_firewall(packet, packet_in)


def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Firewall(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
