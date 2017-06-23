from mininet.topo import Topo

class MyTopo( Topo ):
    "simple topology example."
    def __init__( self ):
        "Creat custom topo."
        

        # Initialize topology
        Topo.__init__( self )

        # Add hots and switches with ip and mac
        host1 = self.addHost( 'h1', ip='10.0.0.1', mac='00:00:00:00:00:01' )
        host2 = self.addHost( 'h2', ip='10.0.0.2', mac='00:00:00:00:00:02' )
        host3 = self.addHost( 'h3', ip='10.0.0.3', mac='00:00:00:00:00:03' )
        host4 = self.addHost( 'h4', ip='10.0.0.4', mac='00:00:00:00:00:04' )
        switch1 = self.addSwitch( 's1' )
        switch2 = self.addSwitch( 's2' )
        switch3 = self.addSwitch( 's3' )
        switch4 = self.addSwitch( 's4' )      
 
        # Add links set the port they used
        self.addLink( host1, switch1,1,1 )
        self.addLink( host2, switch2,1,1 )
        self.addLink( host3, switch3,1,1 )
        self.addLink( host4, switch4,1,1 )
        self.addLink( switch1, switch2,2,3)
        self.addLink( switch2, switch3,2,3)
        self.addLink( switch3, switch4,2,3)
        self.addLink( switch4, switch1,2,3)

topos = { 'mytopo': ( lambda: MyTopo() ) }
