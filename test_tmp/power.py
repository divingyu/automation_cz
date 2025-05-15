import time

from common.operation import *

if __name__ == '__main__':
    serv_resource = []
    try:
        sgnb_a = SgnbServ(rbc.get_sgnb_cfg(), rbc.get_sgnb_name(0))
        sgnb_a.connet_target_sever()
        serv_resource.append(sgnb_a)
        sgnb_b = SgnbServ(rbc.get_sgnb_cfg(1),rbc.get_sgnb_name(1))
        sgnb_b.connet_target_sever()
        serv_resource.append(sgnb_b)
        update_server_time(serv_resource)
        # fully_automated_upgrade_sgnb_version(sgnb_a)
        # fully_automated_upgrade_sgnb_version(sgnb_b)
        for sgnb in serv_resource:
            sgnb.stop_sgnb_process()
        for sgnb in serv_resource:
            sgnb.start_sgnb_process(new_architecture=True, is_copy_cfg=False)
        sgnb_a.start_sgnb_scf()
        print(sgnb_a.execuate_scf_cmd('0'))
        print(sgnb_a.execuate_scf_cmd('0'))
        print(sgnb_a.execuate_scf_cmd('4'))
        sgnb_a.telnet_L3()
        print(sgnb_a.execuate_l3_cmd('showCellStatus'))
        print(sgnb_a.execuate_l3_cmd('show_beam_pattern'))
        print(sgnb_a.execuate_l3_cmd('showPhyCellStatus'))
        time.sleep(5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Exiting the program.")
    finally:
        for sgnb in serv_resource:
            sgnb.stop_sgnb_process()
        ####清理log####
        clean_trace(serv_resource)
        closed_ssh(serv_resource)