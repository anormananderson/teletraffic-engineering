from ryu.app import simple_switch_stp_13
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.lib import stplib
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event

class ProposedSwitch(simple_switch_stp_13.SimpleSwitch13):
    """Simple custom controller to implement both F-switch and S-switch behaviour. Inherits from simple_switch_stp_13.SimpleSwitch13.

    Overrides:
    - _switch_enter_handler
    - _packet_in_handler

    S-switches:
    - forward hardcoded traffic classes to the appropriate F-switch (which is directly connected in the underlying topology).

    F-switches:
    - hardcode forwarding behaviour and drop rules.
    - perform forwarding based on IP.
    - have 'normal' forwarding behaviour besides dropping the appropriate packets.
    """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProposedSwitch, self).__init__(*args, **kwargs)

    @set_ev_cls(event.EventSwitchEnter)
    def _switch_enter_handler(self, ev):
        dp = ev.switch.dp
        dpid = dp.id
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # Parse S-switch (dpid=1X) differently than F-switch (dpid=2X)
        if dpid > 0xA and dpid < 0x20: # S-switch: fwd based on traffic class
            # 1. Match the IP addr to decide which F-switch should receive
            # 2. Forward to port F-switch is attached on

            # define traffic classes
            traffic_class_a = '10.0.0.0/24'
            traffic_class_b = '10.0.1.0/24'
            # traffic class A: we need to fwd dst packets only
            match = parser.OFPMatch(ipv4_dst=traffic_class_a)
            actions = [parser.OFPActionOutput(1)] # f-switch 1 is port 1
            self.add_flow(dp, 1, match, actions)
            # traffic class B: we need to fwd dst packets only
            match = parser.OFPMatch(ipv4_dst=traffic_class_b)
            actions = [parser.OFPActionOutput(2)] # f-switch 2 is port 2
            self.add_flow(dp, 1, match, actions)
        elif dpid > 0x1A: # F-switch: filter traffic
            if dpid == 0x21: # F-switch #1: drop SSH and HTTPS traffic
                for tcp_port in (22, 443):
                    match = parser.OFPMatch(eth_type=0x0800, # must specify IPv4
                                            ip_proto=6, # only TCP
                                            tcp_dst=tcp_port)
                    inst = [parser.OFPInstructionActions(ofp.OFPIT_CLEAR_ACTIONS, [])]
                    mod = parser.OFPFlowMod(datapath=dp, priority=2,
                                            match=match, instructions=inst)
                    dp.send_msg(mod)
            elif dpid == 0x22: # F-switch #2: fwd all traffic
                pass

    @set_ev_cls(stplib.EventPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        super()._packet_in_handler(ev)

