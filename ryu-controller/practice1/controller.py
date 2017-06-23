from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
# you may import more libs here, but the above libs should be enough

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
 
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        # arp table: for searching
        self.arp_table={}
        self.arp_table["10.0.0.1"] = "00:00:00:00:00:01"
        self.arp_table["10.0.0.2"] = "00:00:00:00:00:02"
        self.arp_table["10.0.0.3"] = "00:00:00:00:00:03"
        self.arp_table["10.0.0.4"] = "00:00:00:00:00:04"

   
  
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Insert Static rule
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Installing static rules to process TCP/UDP and ICMP and ACL
        dpid = datapath.id  # classifying the switch ID
        if dpid == 1: # switch S1
            #10.0.0.1 is dst ip address, 1 is switch port number
            # for switch 1, what port number should choose to forward that dst address
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.1', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.2', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.3', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.4', 10, 3)
            


            ### implement icmp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4', 10, 3)

            ### implement udp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.1', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.2', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.3', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.4', 10, 3)

            # implement ACL rules
            # this rule directs the TCP packets from h1 to h3 to the controller
            match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                    ipv4_src = '10.0.0.1',
                                    ipv4_dst = '10.0.0.3',
                                    ip_proto = inet.IPPROTO_TCP)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 30, match, actions)  
            
            match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                    ipv4_src = '10.0.0.3',
                                    ipv4_dst = '10.0.0.1',
                                    ip_proto = inet.IPPROTO_TCP)
            actions = [parser.OFPActionOutput(port=1)]
            self.add_flow(datapath, 30, match, actions) 


            # this rule directs the TCP packets from h3 to h1 to the controller
#            match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
#                                    ipv4_src = '10.0.0.3',
#                                    ipv4_dst = '10.0.0.1',
#                                    ip_proto = inet.IPPROTO_TCP)
#            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
#                                              ofproto.OFPCML_NO_BUFFER)]
#            self.add_flow(datapath, 30, match, actions)  


        elif dpid == 2: # switch S2
            ### implement icmp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1', 10, 3)

            ### implement icmp fwding
            #there is no icmp packets flowing on this switch!

            ### implement udp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.1', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.2', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.3', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.4', 10, 3)

        elif dpid == 3: # switch S3
            ### implement tcp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.1', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.3', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.2', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_TCP, '10.0.0.4', 10, 3)
            ### implement icmp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4', 10, 2)
            ### implement udp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.1', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.3', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.2', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.4', 10, 2)
            ### implement ACL 
            ### drop UDP from 10.0.0.2 to 10.0.0.3 without notification
            # this rule directs the TCP packets from h1 to h3 to the controller
            match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                    ipv4_src = '10.0.0.2',
                                    ipv4_dst = '10.0.0.3',
                                    ip_proto = inet.IPPROTO_UDP)
            actions = []
            self.add_flow(datapath, 30, match, actions)  #add a flow to controller

        elif dpid == 4: # switch S4
            ### implement icmp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4', 10, 1)
            self.add_layer4_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1', 10, 2)

            ### implement icmp fwding
            #there is no icmp packets flowing on this switch!

            ### implement udp fwding
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.1', 10, 2)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.2', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.3', 10, 3)
            self.add_layer4_rules(datapath, inet.IPPROTO_UDP, '10.0.0.4', 10, 1)

        else:
            print "wrong switch"
    

    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ethertype = eth.ethertype

        # process ARP 
        if ethertype == ether.ETH_TYPE_ARP:
            self.handle_arp(datapath, in_port, pkt)
            return

        # process IP
        if ethertype == ether.ETH_TYPE_IP:
            self.handle_ip(datapath, in_port, pkt)
            return

    # Member methods you can call to install TCP/UDP/ICMP fwding rules
    def add_layer4_rules(self, datapath, ip_proto, ipv4_dst = None, priority = 1, fwd_port = None):
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(fwd_port)]
        match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                ip_proto = ip_proto,
                                ipv4_dst = ipv4_dst)
        self.add_flow(datapath, priority, match, actions)

    # Member methods you can call to install general rules
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    
    def handle_arp(self, datapath, in_port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # parse out the ethernet and arp packet
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        # obtain the MAC of dst IP  
        arp_resolv_mac = self.arp_table[arp_pkt.dst_ip]

        ### generate the ARP reply msg, please refer RYU documentation
        ### the packet library section

        ether_hd = ethernet.ethernet(dst = eth_pkt.src, 
                                src = arp_resolv_mac, 
                                ethertype = ether.ETH_TYPE_ARP);
        arp_hd = arp.arp(hwtype=1, proto = 2048, hlen = 6, plen = 4,
                         opcode = 2, src_mac = arp_resolv_mac, 
                         src_ip = arp_pkt.dst_ip, dst_mac = eth_pkt.src,
                         dst_ip = arp_pkt.src_ip);
        arp_reply = packet.Packet()
        arp_reply.add_protocol(ether_hd)
        arp_reply.add_protocol(arp_hd)
        arp_reply.serialize()
       



        
        # send the Packet Out mst to back to the host who is initilaizing the ARP
        actions = [parser.OFPActionOutput(in_port)];
        out = parser.OFPPacketOut(datapath, ofproto.OFP_NO_BUFFER, 
                                  ofproto.OFPP_CONTROLLER, actions,
                                  arp_reply.data)
        datapath.send_msg(out)

    def handle_ip(self, datapath, in_port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        ipv4_pkt = pkt.get_protocol(ipv4.ipv4) # parse out the IPv4 pkt

        if datapath.id == 1 and ipv4_pkt.proto == inet.IPPROTO_TCP:
            tcp_pkt = pkt.get_protocol(tcp.tcp) # parser out the TCP pkt
            eth_pkt = pkt.get_protocol(ethernet.ethernet)
            #if (tcp_pkt.bits) % 4 == 2:


            tcp_hd = tcp.tcp(ack=tcp_pkt.seq+1, src_port = tcp_pkt.dst_port, dst_port = tcp_pkt.src_port, bits=20)
            ip_hd = ipv4.ipv4(dst= ipv4_pkt.src, src= ipv4_pkt.dst, proto=ipv4_pkt.proto)
            ether_hd = ethernet.ethernet(ethertype = ether.ETH_TYPE_IP, dst = eth_pkt.src, src = eth_pkt.dst)
            tcp_rst_ack = packet.Packet()
            tcp_rst_ack.add_protocol(ether_hd)
            tcp_rst_ack.add_protocol(ip_hd)
            tcp_rst_ack.add_protocol(tcp_hd)
            tcp_rst_ack.serialize()


            ### generate the TCP packet with the RST flag set to 1
            ### packet generation is similar to ARP,
            ### but you need to generate ethernet->ip->tcp and serialize it
            
        # send the Packet Out mst to back to the host who is initilaizing the ARP
            actions = [parser.OFPActionOutput(in_port)];
            out = parser.OFPPacketOut(datapath, ofproto.OFP_NO_BUFFER, 
                                      ofproto.OFPP_CONTROLLER, actions,
                                      tcp_rst_ack.data)
            datapath.send_msg(out)
       
