#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
class MyTopology(Topo):
  """
  A basic topology
  """
  def __init__(self):
    Topo.__init__(self) 
    # Set Up Topology Here
    switch1 = self.addSwitch('Switch1') ## Adds a Switch
    switch2 = self.addSwitch('Switch2') ## Adds a Switch
    switch3 = self.addSwitch('Switch3') ## Adds a Switch
    switch4 = self.addSwitch('Switch4') ## Adds a Switch
    siri = self.addHost('Siri', ip = '10.0.0.5/24') ## Adds a Host
    alexa = self.addHost('Alexa', ip = '10.0.0.5/24' ) ## Adds a Host
    desktop = self.addHost('Desktop', ip ='10.0.0.1/24' ) ## Adds a Host
    smartTV = self.addHost('SmartTV', ip ='10.0.0.3/24' ) ## Adds a Host
    fridge = self.addHost('Fridge', ip ='10.0.0.4/24' ) ## Adds a Host
    server = self.addHost('Server', ip = '10.0.0.2/24') ## Adds a Host
    self.addLink(siri, switch3) ## Add a link
    self.addLink(alexa, switch3) ## Add a link
    self.addLink(switch2, switch3) ## Add a link
    self.addLink(desktop, switch2) ## Add a link
    self.addLink(switch2, switch4) ## Add a link
    self.addLink(server, switch4) ## Add a link
    self.addLink(switch1, switch2) ## Add a link
    self.addLink(smartTV, switch1) ## Add a link
    self.addLink(fridge, switch1) ## Add a link

if __name__ == '__main__':
  """
  If this script is run as an executable (by chmod +x), this is
  what it will do
  """
  topo = MyTopology() ## Creates the topology
  net = Mininet( topo=topo ) ## Loads the topology
  net.start() ## Starts Mininet
  # Commands here will run on the simulated topology
  CLI(net)
  net.stop() ## Stops Mininet
