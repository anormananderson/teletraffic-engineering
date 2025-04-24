from ryu.app import simple_switch_stp_13
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.lib import stplib
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event

class ComparisonSwitch(simple_switch_stp_13.SimpleSwitch13):
    """Simple custom controller to implement switches which filter traffic. Inherits from simple_switch_stp_13.SimpleSwitch13.

    Overrides:
    - _switch_enter_handler
    - _packet_in_handler
    """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ComparisonSwitch, self).__init__(*args, **kwargs)

    @set_ev_cls(event.EventSwitchEnter)
    def _switch_enter_handler(self, ev):
        dp = ev.switch.dp
        dpid = dp.id
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        if dpid == 0x24: # s4f
            match = parser.OFPMatch(in_port=1) # allow pass-through from s3f
            actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
            mod = parser.OFPFlowMod(
                datapath=dp,
                priority=100,
                match=match,
                instructions=inst
            )
            dp.send_msg(mod)

            drop_match = parser.OFPMatch() # Matches all packets
            drop_inst = [] # No actions = drop
            drop_mod = parser.OFPFlowMod(
                datapath=dp,
                priority=0,
                match=drop_match,
                instructions=drop_inst
            )
            dp.send_msg(drop_mod) # drop all other packets!! (not working)
        elif dpid == 0x21:
            # drop SSH and HTTPS traffic
            for tcp_port in (22, 443):
                # outgoing
                match = parser.OFPMatch(eth_type=0x0800, # must specify IPv4
                                        ip_proto=6, # only TCP
                                        ipv4_dst='10.0.0.0/24', # filter one subnet
                                        tcp_dst=tcp_port)
                inst = [parser.OFPInstructionActions(ofp.OFPIT_CLEAR_ACTIONS, [])]
                mod = parser.OFPFlowMod(datapath=dp, priority=100,
                                        match=match, instructions=inst)
                dp.send_msg(mod)

                # incoming
                match = parser.OFPMatch(eth_type=0x0800, # must specify IPv4
                                        ip_proto=6, # only TCP
                                        ipv4_src='10.0.0.0/24', # filter one subnet
                                        tcp_dst=tcp_port)
                inst = [parser.OFPInstructionActions(ofp.OFPIT_CLEAR_ACTIONS, [])]
                mod = parser.OFPFlowMod(datapath=dp, priority=100,
                                        match=match, instructions=inst)
                dp.send_msg(mod)

        else:
            pass # for simplicity we only install rules in s1f

    @set_ev_cls(stplib.EventPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        super()._packet_in_handler(ev)

