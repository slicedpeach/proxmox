import api
import time
controller = api.Proxmoxadmin()

controller.create_vms()

controller.start_vms("C:/Users/saman/Desktop/proxmox/start_vms/vms.txt")
time.sleep(10)
controller.suspend_vms("C:/Users/saman/Desktop/proxmox/suspend_vms/vms.txt")
time.sleep(10)
controller.resume_vms("C:/Users/saman/Desktop/proxmox/resume_vms/vms.txt")
time.sleep(10)
controller.extend_vms()
time.sleep(10)
controller.extend2_vms()
time.sleep(10)
controller.extend3_vms()
time.sleep(10)
controller.extend3_vms()
time.sleep(10)
controller.extend2_vms(upgrade=1)
time.sleep(10)
controller.extend3_vms(upgrade=1)




