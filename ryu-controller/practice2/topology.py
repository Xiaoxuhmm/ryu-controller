"""
Topooly for practice2

    S1    S2
 (1)| \(2)/|(1)
    |  \/  |
    |  /\  |
 (2)| /  \ |(3)
    S3    S4
    |(1)   | (1)
    |(1)   | (1)
    H1     H2

"""

from mininet.topo import Topo

class MyTopo( Topo ):

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        # Hosts
        leftHost        = self.addHost( 'h1', ip='10.0.0.1', mac='00:00:00:00:00:01' )
        rightHost       = self.addHost( 'h2', ip='10.0.0.2', mac='00:00:00:00:00:02' )
        # Switches
        leftCoreSwitch  = self.addSwitch( 's1' )
        rightCoreSwitch = self.addSwitch( 's2' )
        leftEdgeSwitch  = self.addSwitch( 's3' )
        righEdgetSwitch = self.addSwitch( 's4' )

        # Add links
        self.addLink( leftHost       , leftEdgeSwitch , 1, 1 )
        self.addLink( rightHost      , righEdgetSwitch, 1, 1 )
        self.addLink( leftEdgeSwitch , leftCoreSwitch , 2, 1 )
        self.addLink( leftEdgeSwitch , rightCoreSwitch, 3, 2 )
        self.addLink( righEdgetSwitch, leftCoreSwitch , 3, 2 )
        self.addLink( righEdgetSwitch, rightCoreSwitch, 2, 1 )


topos = { 'mytopo': ( lambda: MyTopo() ) }
