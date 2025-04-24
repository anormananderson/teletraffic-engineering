from mininet.topo import Topo

class ProposedTopo(Topo):
    """Basic test topology with S- and F-switches.

    [ s1s ]===========================================.
      ,----'          |               |               |
    [ s1f ]         [ s2f ]         [ s3f ]         [ s4f ]
      |               |               |               |
      |               |               |               |
    [ s1 ]===.      [ s2 ]===.      [ s3 ]===.      [ s4 ]===.
    [ r1h1 ]-|      [ r2h1 ]-|      [ r3h1 ]-|      [ r4h1 ]-|
    [ r1h2 ]-|      [ r2h2 ]-|      [ r3h2 ]-|      [ r4h2 ]-|
    [ r1h3 ]-|      [ r2h3 ]-|      [ r3h3 ]-|      [ r4h3 ]-|
    [ r1h4 ]-'      [ r2h4 ]-'      [ r3h4 ]-'      [ r4h4 ]-'
    """

    def build(self):
        tor_switches = []
        for rack in range(1, 5):
            # Create ToR switch
            tor = self.addSwitch('s%d' % rack, dpid='%x' % rack)
            tor_switches.append(tor)
            # Each host in rack
            for host in range(1, 5):
                host = self.addHost('r%dh%d' % (rack, host), ip='10.0.%d.%d' % (rack-1, host))
                # Add links between each host and ToR
                self.addLink(tor, host)

        # Extra switches required by construction
        # Create a S-switch, dpid always starts with '1'
        s1s = self.addSwitch('s1s', dpid='11')

        # Create two F-switches, dpid always starts with '2'
        s1f = self.addSwitch('s1f', dpid='21')
        s2f = self.addSwitch('s2f', dpid='22')
        s3f = self.addSwitch('s3f', dpid='23')
        s4f = self.addSwitch('s4f', dpid='24')

        # Connect S and F switches to topology
        self.addLink(s1s, s1f, port1=1, port2=1)
        self.addLink(s1s, s2f, port1=2, port2=1)
        self.addLink(s1s, s3f, port1=3, port2=1)
        self.addLink(s1s, s4f, port1=4, port2=1)

        self.addLink(s1f, tor_switches[0], port1=2)
        self.addLink(s2f, tor_switches[1], port1=2)
        self.addLink(s3f, tor_switches[2], port1=2)
        self.addLink(s4f, tor_switches[3], port1=2)

# Allows the file to be imported using `mn --custom <filename> --topo mybasic`
topos = {
    'proposed': ProposedTopo
}

