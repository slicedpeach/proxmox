from proxmoxer import ProxmoxAPI
import pymongo
import time
import datetime
import os
import requests
from dotenv import load_dotenv
load_dotenv()
MONGOHOST = os.getenv('MONGOHOST')
PROXHOST = os.getenv('PROXHOST')
PROXUSER = os.getenv('PROXUSER')
PROXPASS = os.getenv('PROXPASS')
PROXTOKENNAME = os.getenv('PROXTOKENNAME')
PROXTOKEN = os.getenv('PROXTOKENVAL')




class Proxmoxadmin:
    def __init__(self):
        self.proxmox = ProxmoxAPI(
                    host = PROXHOST, user = PROXUSER,  password = PROXPASS, verify_ssl = False, token_name  = PROXTOKENNAME, token_value = PROXTOKEN
                    )
        self.mongoclient = pymongo.MongoClient(MONGOHOST)
    
    def get_logs(self,vmid):
        
        while(1):
            tasks = self.proxmox.cluster.tasks.get()
            
            for task in tasks:
                print(type(task["id"]))
                if task["id"]==str(vmid) and task["type"] == 'qmrestore' and 'endtime' in list(task.keys()):
                    print(f"restore of vm with id {vmid} complete!")
                    return
            print("still waiting!")
            time.sleep(10)

    
    def create_vms(self):
        db = self.mongoclient["proxmox"]
        creation_collection = db["vm requests"]
        requests = creation_collection.find()

        for req in requests:
            del req["data"]["datecreated"]
            valid_time = req["data"]["exp"]
            del req["data"]["exp"]
            del req["data"]["dateexp"]
            l=self.proxmox.nodes("salmanzadeh").qemu.post(vmid=req["vmid"],**req["data"])
            name = req["data"]["name"]
            print(f"vm {name} created")
            creation_collection.update_one({"vmid":req["vmid"]},{"$set":{"data.datecreated":datetime.datetime.now(),
                                                        "data.dateexp":datetime.datetime.now()+datetime.timedelta(days=valid_time)}})
            self.get_logs(req["vmid"])
            self.replace_disk(req["vmid"], req["disk"])

    
    def resume_vms(self,startfile):
        vmids = []
        f = open(startfile,"r")

        for vmid in f:
            vmids.append(vmid)
        
        for vmid in vmids:
            self.proxmox.nodes("salmanzadeh").qemu(vmid).status.resume.post()

    
    def start_vms(self,startfile):
        vmids = []
        f = open(startfile,"r")

        for vmid in f:
            vmids.append(vmid)
        
        for vmid in vmids:
            self.proxmox.nodes("salmanzadeh").qemu(vmid).status.start.post()


    def suspend_vms(self,startfile):
        vmids = []
        f = open(startfile,"r")

        for vmid in f:
            vmids.append(vmid)
        
        for vmid in vmids:
            self.proxmox.nodes("salmanzadeh").qemu(vmid).status.suspend.post()


    def replace_disk(self, vmid, disk):
        vm = self.proxmox.nodes("salmanzadeh").qemu(vmid).config.get()

        unused_disks=[]
        scsi_disks=[]
        for s in vm.keys():
            if "scsi" in s[0:5] and "hw" not in s:
                scsi_disks.append(s)
        print(unused_disks)

        if len(scsi_disks)>0:
            l=self.proxmox.nodes("salmanzadeh").qemu(vmid).config.put(delete=scsi_disks)
        mount = self.proxmox.nodes("salmanzadeh").qemu(vmid).config.post(scsi0=disk)

        for s in vm.keys():
            if "unused" in s:
                unused_disks.append(s)

        if len(unused_disks)>0:
            l=self.proxmox.nodes("salmanzadeh").qemu(vmid).config.put(delete=unused_disks)
        print("disk succesfully replaced!")


    def extend_vms(self):
        db = self.mongoclient["proxmox"]
        creation_collection = db["vm requests"]
        f = open("C:/Users/saman/Desktop/proxmox/extend_vms/vms.txt","r")
        for line in f:
            vm,t = line.split()
            res = creation_collection.find({"vmid":int(vm)})
            creation_collection.update_one({"vmid":int(vm)},{"$set":{"data.dateexp":datetime.datetime.now()+datetime.timedelta(days=int(t))}})


    def extend2_vms(self,upgrade=0):
        db = self.mongoclient["proxmox"]
        extension2_collection = db["vm_extend2"]
        creation_collection = db["vm requests"]
        requests = extension2_collection.find()
        l=None
        for req in requests:
            self.proxmox.nodes("salmanzadeh").qemu(req["vmid"]).status.stop.post()

            l=self.proxmox.nodes("salmanzadeh").qemu(req["vmid"]).config.post(**req["data"])
            if upgrade == 0:
                creation_collection.update_one({"vmid":req["vmid"]},{"$set":{"data.dateexp":datetime.datetime.now()+datetime.timedelta(days=req["extension"])}})
            self.replace_disk(req["vmid"], req["disk"])
            
            self.proxmox.nodes("salmanzadeh").qemu(req["vmid"]).status.start.post()


    def extend3_vms(self,upgrade=0):
        db = self.mongoclient["proxmox"]
        extension3_collection = db["vm_extend3"]
        creation_collection = db["vm requests"]
        requests = extension3_collection.find()
        for req in requests:
            if upgrade == 0:
                creation_collection.update_one({"vmid":req["vmid"]},{"$set":{"data.dateexp":datetime.datetime.now()+datetime.timedelta(days=req["extension"])}})
            self.replace_disk(req["vmid"], req["disk"])
    





proxmox = Proxmoxadmin()
#proxmox.create_vms()
#proxmox.start_vms("start_vms/vms.txt")
#proxmox.suspend_vms("suspend_vms/vms.txt")
#proxmox.resume_vms("resume_vms/vms.txt")
#proxmox.extend_vms()
#proxmox.extend2_vms()
#proxmox.extend3_vms()
#proxmox.extend2_vms(upgrade=1)
#proxmox.extend3_vms()
