#!/usr/bin/python
import json
import re
import subprocess

cmd = "juju status --format json"
res = subprocess.check_output(cmd.split(" "))
juju_dict = json.loads(res)

# This is Test code
#f = open('./test-json/juju.json', 'read')
#juju_dict = json.load(f)

js_out = {}
k0 = juju_dict.keys()[0] #applications
k2 = juju_dict.keys()[2] #machines
metadata = {'_meta':{'hostvars':{}}}
ha_flag = ''

# Get a physical machine that has IP
phy_machines = {k2:[]}
for i in juju_dict[k2].keys():
    phy_machines[k2].append(juju_dict[k2][i]['dns-name'])

js_out.update(phy_machines)

# Get an application that has IP
for i in juju_dict[k0].keys(): # application name. ex) keystone
    application_list = {i:[]}
    check_units = juju_dict[k0][i].keys()
    if 'units' in check_units:
        for j in juju_dict[k0][i]['units'].keys(): # unit name. ex) keystone/0
            unit_machine = juju_dict[k0][i]['units'][j]['machine']

            # Check unit that has ***-hacluster
            if 'subordinates' in juju_dict[k0][i]['units'][j].keys():
                ha_check = juju_dict[k0][i]['units'][j]["subordinates"].keys()[0]
                if 'ha' in ha_check:
                    ha_flag = 'true'
                else:
                    ha_flag = "false"

            machine_id = re.sub(r'/.*', "", unit_machine)
            # Check Machine or Container
            if "/" in unit_machine:

                ip = juju_dict[k2][machine_id]["containers"][unit_machine]["ip-addresses"][0]
                application_list[i].append(ip)
            else:
                ip = juju_dict[k2][unit_machine]["ip-addresses"][0]
                application_list[i].append(ip)

            unit_list = {j:ip}

            hostvars = {}
            for k, v in unit_list.items(): #k=unit v=ipaddress
                # hostvars add new key
                hostvars[v] = {'hostname':v, 'ip_address':v, 'juju_name':k, 'ha':ha_flag, 'node':machine_id}
                metadata['_meta']['hostvars'].update(hostvars)
            js_out.update(metadata)
            js_out.update(application_list)

# Get all that has IP
all_hosts = {'allhosts':[]}
for k in js_out.keys():
    if '/' not in k and '_meta' not in k:
        for v in js_out[k]:
            all_hosts['allhosts'].append(v)
js_out.update(all_hosts)
print(json.dumps(js_out))

