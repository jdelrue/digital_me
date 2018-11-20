import random

from Jumpscale import j

DEFAULT_CORE_NR = 2
DEFAULT_MEM_SIZE = 2048

gedis_client = None
countries = []
farmers = []


def chat(bot):
    """
    a chatbot to reserve zos vm
    :param bot:
    :return:
    """

    def country_list():
        report = ""
        for country in countries:
            report += "- %s\n" % country
        bot.md_show(report)

    def farmer_register():
        jwttoken = bot.string_ask("Please enter your JWT")
        farmer_name = bot.string_ask("Enter farmer name as stated into the directory:")
        email_address = bot.string_ask("Enter farmer email:")
        mobile_number = bot.string_ask("Enter farmer mobile:")
        farmer_pub_key = bot.text_ask("Public key for the farmer:")
        farmer_iyo = bot.string_ask("Enter IYO organization name:", validate={"required": True})
        gedis_client.farmer.farmer_register(jwttoken, farmer_name, email_addresses=[email_address],
                                            mobile_numbers=[mobile_number], pubkey=farmer_pub_key)

    def farmers_get():
        report = ""
        for farmer in farmers:
            report += "- %s\n" % farmer.name
        bot.md_show(report)

    def node_find():
        fields = {
            "Country": {"type": "list", "name": "country", "choices": [country for country in countries]},
            "Farmer name": {"type": "list", "name": "farmer_name", "choices": [farmer.name for farmer in farmers]},
            "Number of cores": {"type": "int", "name": "cores_min_nr"},
            "Minimum memory in MB": {"type": "int", "name": "mem_min_mb"},
            "SSD min in GB": {"type": "int", "name": "ssd_min_gb"},
            "HD min in GB": {"type": "int", "name": "hd_min_gb"},
        }
        selected = bot.multi_choice("please select fields you want to find with", list(fields.keys()))
        selected = j.data.serializers.json.loads(selected)
        kwargs = {}
        for field in selected:
            if fields[field]["type"] == "int":
                kwargs[fields[field]["name"]] = bot.int_ask("Enter {}".format(field))
            else:
                kwargs[fields[field]["name"]] = bot.drop_down_choice("Enter {}".format(field), fields[field]["choices"])
        return kwargs

    def ubuntu_reserve(jwt_token, node, vm_name, zerotier_token, cores, memory):
        pub_ssh_key = bot.string_ask("Enter your public ssh key")
        zerotier_network = bot.string_ask("Enter the extra zerotier network id you need the vm to join:")
        res = gedis_client.farmer.ubuntu_reserve(jwttoken=jwt_token, node=node, vm_name=vm_name, memory=memory,
                                                 cores=cores, zerotier_network=zerotier_network,
                                                 zerotier_token=zerotier_token, pub_ssh_key=pub_ssh_key)
        report = """## Ubuntu reserved
    # you have successfully registered a zos vm
    - robot url = {robot_url}
    - service secret = {service_secret}
    - ZT Network 1 = {zt_network1}
    - ZT IP 1 = {ip_addr1}
    - ZT Network 2 = {zt_network2}
    - ZT IP 2 = {ip_addr2}
""".format(robot_url=res.node_robot_url, service_secret=res.service_secret, zt_network1=res.zt_network1,
           zt_network2=res.zt_network2, ip_addr1=res.ip_addr1, ip_addr2=res.ip_addr2)
        bot.md_show(report)

    def zos_reserve(jwttoken, node, vm_name, zerotier_token, memory, cores):
        organization = bot.string_ask("Enter your itsyou.online organization")
        res = gedis_client.farmer.zos_reserve(jwttoken, node, vm_name, memory, cores, zerotier_token, organization)
        report = """## ZOS reserved
# you have succesfully registered a zos vm
    - robot url = {robot_url}
    - service secret = {service_secret}
    - ip address = {ip_address}
    - port = {port}""".format(robot_url=res.robot_url, service_secret=res.service_secret,
                              ip_address=res.ip_address, port=res.redis_port)
        bot.md_show(report)
        bot.redirect("https://threefold.me")

    def web_gateway_http_proxy_delete():
        web_gateways = gedis_client.farmer.web_gateways_get().res
        jwttoken = bot.string_ask("Please enter your JWT, "
                                  "(click <a target='_blank' href='/client'>here</a> to get one)",
                                  validate={"required": True})
        web_gateway_name = bot.drop_down_choice("Choose the web gateway you need to delete your domain from: ",
                                                [web_gateway.name for web_gateway in web_gateways])
        web_gateway = {}
        for gateway in web_gateways:
            if gateway.name == web_gateway_name:
                web_gateway = gateway
        rule_name = bot.string_ask("Enter the forwarding rule name that you have configured:",
                                   validate={"required": True})
        gedis_client.farmer.web_gateway_delete_host(jwttoken, web_gateway=web_gateway, rule_name=rule_name)

    def web_gateway_http_proxy_set():
        web_gateways = gedis_client.farmer.web_gateways_get().res
        jwttoken = bot.string_ask("Please enter your JWT, "
                                  "(click <a target='_blank' href='/client'>here</a> to get one)",
                                  validate={"required": True})
        web_gateway_name = bot.drop_down_choice("Choose the web gateway you need to add your domain to it: ",
                                                [web_gateway.name for web_gateway in web_gateways],
                                                validate={"required": True})
        web_gateway = {}
        for gateway in web_gateways:
            if gateway.name == web_gateway_name:
                web_gateway = gateway
        domain = bot.string_ask("Enter domain you need to configure i.e. mywebsite.test.com",
                                validate={"required": True})
        backends = bot.string_ask("Enter comma separated backends you need to point to: "
                                  "i.e. http://192.168.1.1:8000,http://192.168.1.2:5000", validate={"required": True})
        backends = [backend.strip() for backend in backends.split(",")]
        gedis_client.farmer.web_gateway_add_host(jwttoken, web_gateway=web_gateway, domain=domain, backends=backends)

    def web_gateway_list_hosts():
        jwttoken = bot.string_ask("Please enter your JWT, "
                                  "(click <a target='_blank' href='/client'>here</a> to get one)",
                                  validate={"required": True})
        res = gedis_client.farmer.web_gateway_list_hosts(jwttoken).res
        report = """| Rule Name    |                Domains                       |             Backends                  |   Gateway    | 
|:-------------:|:---------------------------------------:|:--------------------------------------------:|:-----------------------------:|  
"""
        for rule in res:
            report += """|{rule_name}|{domains}|{backends}|{webgateway_name}| 
""".format(rule_name=rule.rule_name, domains=",".join(rule.domains),
           backends=", ".join(rule.backends), webgateway_name=rule.webgateway_name)
        bot.md_show(report)

    def web_gateway_register():
        jwttoken = bot.string_ask("Please enter your JWT, "
                                  "(click <a target='_blank' href='/client'>here</a> to get one)",
                                  validate={"required": True})
        name = bot.string_ask("Enter gateway name:", validate={"required": True})
        service_name = bot.string_ask("Enter gateway service name that you have installed in zrobot:",
                                      validate={"required": True})
        master_domain = bot.string_ask("Enter gateway master domain:", validate={"required": True})
        description = bot.string_ask("Additional description?")
        gedis_client.farmer.web_gateway_register(jwttoken=jwttoken, name=name, service_name=service_name,
                                                 description=description, master_domain=master_domain)

    def zdb_reserve(jwttoken, node):
        zdb_name = bot.string_ask("Please enter your ZDB name:")
        disk_type = bot.single_choice("Please choose the disk type:", ["ssd", "hdd"])
        disk_size = bot.int_ask("Please enter the disk size:")
        namespace_name = bot.string_ask("Please enter your namespace name:")
        namespace_size = bot.int_ask("Please enter the namespace size:")
        namespace_secret = bot.password_ask("Please enter the namespace secret:")
        res = gedis_client.farmer.zdb_reserve(jwttoken, node, zdb_name, namespace_name, disk_type, disk_size,
                                              namespace_size, namespace_secret)
        report = """## ZDB reserved
        # you have successfully registered a Zero DB
            - robot url = {robot_url}
            - service secret = {service_secret}
            - ip address = {ip_address}
            - storage_ip = {storage_ip}
            - port = port""".format(robot_url=res.robot_url, service_secret=res.service_secret,
                                    ip_address=res.ip_address, port=res.port, storage_ip=res.storage_ip)
        bot.md_show(report)
        bot.redirect("https://threefold.me")

    def reserve_vm():
        jwt_token = bot.string_ask("Please enter your JWT, "
                                   "(click <a target='_blank' href='/client'>here</a> to get one)")
        while True:
            node_filters = node_find()
            candidate_nodes = gedis_client.farmer.node_find(**node_filters)
            if candidate_nodes.res:
                break
            bot.md_show("No available nodes with these criteria, please try again")

        node = candidate_nodes.res[random.randint(0, len(candidate_nodes.res) - 1)]
        vm_type = bot.single_choice("what do you want to do", ["Ubuntu", "Zero OS", "Zero DB"])
        if vm_type == "Zero DB":
            zdb_reserve(jwt_token, node)
            return
        vm_name = bot.string_ask("What will you call the vm?")
        zerotier_token = bot.string_ask("Enter your zerotier token:")
        cores = int(node_filters.get('cores_min_nr', DEFAULT_CORE_NR))
        memory = int(node_filters.get('mem_min_mb', DEFAULT_MEM_SIZE))
        if vm_type == "Ubuntu":
            ubuntu_reserve(jwt_token, node, vm_name, zerotier_token, cores, memory)
        elif vm_type == "Zero OS":
            zos_reserve(jwt_token, node, vm_name, zerotier_token, memory=memory, cores=cores)

    def reserve_s3():
        farmer_name = 'bancadati.threefold.grid.farm01'
        storage_type = 'hdd'
        data_plans = {
            "plan 1 (1 data shard and 1 parity shard)":
                {
                    "data_shards": 1,
                    "parity_shards": 1,
                },
            "plan 2  (4 data shard and 2 parity shard)":
                {
                    "data_shards": 4,
                    "parity_shards": 2
                }
        }
        # generate random namespace login and password
        ns_name = j.data.idgenerator.generateXCharID(8)
        ns_password = j.data.idgenerator.generateXCharID(16)
        web_gateways = gedis_client.farmer.web_gateways_get().res
        web_gateway_name = bot.drop_down_choice("Choose the web gateway you need to add your domain to it: ",
                                                [web_gateway.name for web_gateway in web_gateways],
                                                validate={"required": True})
        web_gateway = {}
        for gateway in web_gateways:
            if gateway.name == web_gateway_name:
                web_gateway = gateway
        name = bot.string_ask("Please enter your s3 name", validate={"required": True})
        domain = "{}.{}".format(name, web_gateway.master_domain)
        zt_token = bot.string_ask("Enter your zerotier token:", validate={"required": True})
        zerotier_network = bot.string_ask("Enter the zerotier network id you need the s3 to join:",
                                          validate={"required": True})
        size = bot.int_ask("Enter the total size of S3 in GB", default=10, validate={"required": True})

        plan = bot.single_choice("Choose a plan", list(data_plans.keys()))
        data_shards = data_plans[plan]['data_shards']
        parity_shards = data_plans[plan]['parity_shards']

        minio_login = bot.string_ask("Enter minio login name", default="admin", validate={"required": True})
        minio_password = bot.password_ask("Enter minio password", validate={"required": True, "length_min": 8})
        gedis_client.farmer.s3_reserve(name=name, management_network_id=zerotier_network, size=size,
                                       domain=domain, web_gateway_service=web_gateway.service_name,
                                       farmer_name=farmer_name, data_shards=data_shards,
                                       parity_shards=parity_shards, zt_token=zt_token,
                                       storage_type=storage_type, minio_login=minio_login,
                                       minio_password=minio_password,
                                       ns_name=ns_name, ns_password=ns_password)
        bot.md_show("You can access your s3 using: {}".format(domain))

    def get_gedis_client():
        global gedis_client, countries, farmers
        # Previously configured gedis clients
        gedis_clients = j.clients.gedis.list()
        gedis_client_name = ""
        if gedis_clients:
            gedis_client_name = bot.single_choice(
                "Choose the farmer robot you want to use or choose other to configure new one:",
                gedis_clients + ['other']
            )
        if not gedis_client_name or gedis_client_name == "other":
            gedis_host = bot.string_ask("Enter the farmer robot host ip:")
            gedis_port = bot.int_ask("Enter the farmer robot host port: ")
            gedis_client_name = bot.string_ask("Choose a convenient name for the farmer robot:")
            gedis_client = j.clients.gedis.get(instance=gedis_client_name, data={
                'host': gedis_host,
                'port': gedis_port
            })
        else:
            gedis_client = j.clients.gedis.get(instance=gedis_client_name)
        countries = gedis_client.farmer.country_list().res
        farmers = gedis_client.farmer.farmers_get().res
        return

    def main():
        get_gedis_client()
        methods = {
            "Reserve S3": reserve_s3,
            "Register Domain": web_gateway_http_proxy_set,
            "List Domains": web_gateway_list_hosts,
            "Delete Domain": web_gateway_http_proxy_delete,
            "Register web gateway": web_gateway_register,
        }
        while True:
            choice = bot.single_choice("what do you want to do", [method for method in methods.keys()], reset=True)
            try:
                methods[choice]()
            except Exception as e:
                bot.md_show(str(e))

    main()
