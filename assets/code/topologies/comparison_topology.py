from mininet.topo import Topo
from mininet.link import TCLink

class ComparisonTopo(Topo):
    """
    Basic test topology with four filter switches.
    s1-s4 are connected to both f1 and f4.

      ,----------,====,================,---------------------,
      |        [ f1 ]-+-[ f2 ]--[ f3 ]-+-[ f4 ]===========,  |
      |,--------------+,===============+=================='  |
      ||              ||              ||               |,----'
      ||              ||              ||               ||
    [ s1 ]===.      [ s2 ]===.      [ s3 ]===.       [ s4 ]===.
    [ r1h1 ]-|      [ r2h1 ]-|      [ r3h1 ]-|       [ r4h1 ]-|
    [ r1h2 ]-|      [ r2h2 ]-|      [ r3h2 ]-|       [ r4h2 ]-|
    [ r1h3 ]-|      [ r2h3 ]-|      [ r3h3 ]-|       [ r4h3 ]-|
    [ r1h4 ]-'      [ r2h4 ]-'      [ r3h4 ]-'       [ r4h4 ]-'
    """

    def build(self):
        # Create filtering switches
        s1f = self.addSwitch('s1f', dpid='21')
        s2f = self.addSwitch('s2f', dpid='22')
        s3f = self.addSwitch('s3f', dpid='23')
        s4f = self.addSwitch('s4f', dpid='24')
        # Link filtering switches
        self.addLink(s1f, s2f, port1=1, port2=1)
        self.addLink(s2f, s3f, port1=2, port2=1)
        self.addLink(s3f, s4f, port1=2, port2=1)

        for rack in range(1, 5):
            # Create ToR switch
            tor = self.addSwitch('s%d' % rack, dpid='%x' % rack)
            # Link rack to s1f (for outgoing traffic)
            self.addLink(s1f, tor, cls=TCLink, port2=1)
            # Link s4f to rack (for incoming traffic)
            self.addLink(s4f, tor, cls=TCLink, port2=2)
            # Each host in rack
            for host in range(1, 5):
                host = self.addHost('r%dh%d' % (rack, host), ip='10.0.%d.%d' % (rack-1, host))
                # Add links between each host and ToR
                self.addLink(tor, host)

# Allows the file to be imported using `mn --custom <filename> --topo mybasic`
topos = {
    'comparison': ComparisonTopo
}

