from ncclient import manager
import xmltodict

# Router IP Address is 10.0.15.62
studentID = "66070100"

def get_manager(router_ip):
    return manager.connect(
        host=router_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    )

def create(router_ip):
    m = get_manager(router_ip)
    try:
        netconf_config = f"""
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="create">
            <name>Loopback{studentID}</name>
            <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
            <enabled>true</enabled>
            <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                <address>
                    <ip>172.1.0.1</ip>
                    <netmask>255.255.255.0</netmask>
                </address>
            </ipv4>
        </interface>
    </interfaces>
</config>
"""

        netconf_reply = netconf_edit_config(netconf_config, m)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {studentID} is created successfully using Netconf"
        else:
            # This case might not be hit if an exception is thrown, but is here for safety
            return f"Cannot create: Interface loopback {studentID}"
    except Exception as e:
        # This block will be executed if the interface already exists, because "operation='create'" will cause an error.
        print(f"Error in create (likely because interface exists): {e}")
        return f"Cannot create: Interface loopback {studentID}"
    finally:
        try:
            m.close_session()
        except Exception:
            try:
                # best-effort fallback to transport close if available
                if hasattr(m, 'transport') and hasattr(m.transport, 'close'):
                    m.transport.close()
            except Exception:
                pass


def delete(router_ip):
    m = get_manager(router_ip)
    try:
        netconf_config = f"""
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
            <name>Loopback{studentID}</name>
        </interface>
    </interfaces>
</config>
"""

        netconf_reply = netconf_edit_config(netconf_config, m)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {studentID} is deleted successfully using Netconf"
        else:
            # This case might not be hit if an exception is thrown, but is here for safety
            return f"Cannot delete: Interface loopback {studentID}"
    except Exception as e:
        # This block will be executed if the interface does not exist, because "operation='delete'" on a non-existent interface will cause an error.
        print(f"Error in delete (likely because interface does not exist): {e}")
        return f"Cannot delete: Interface loopback {studentID}"
    finally:
        try:
            m.close_session()
        except Exception:
            try:
                if hasattr(m, 'transport') and hasattr(m.transport, 'close'):
                    m.transport.close()
            except Exception:
                pass


def enable(router_ip):
    # First, check the interface's current status.
    status_result = status(router_ip)
    if "is enabled" in status_result:
        return f"Cannot enable: Interface loopback {studentID}"
    if "No Interface" in status_result:
        return f"Cannot enable: Interface loopback {studentID}"

    m = get_manager(router_ip)
    try:
        netconf_config = f"""
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>Loopback{studentID}</name>
            <enabled>true</enabled>
        </interface>
    </interfaces>
</config>
"""

        # Using "merge" operation, which is the default.
        netconf_reply = netconf_edit_config(netconf_config, m)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {studentID} is enabled successfully using Netconf"
        else:
            return f"Cannot enable: Interface loopback {studentID}"
    except Exception as e:
        print(f"Error in enable: {e}")
        return f"Cannot enable: Interface loopback {studentID}"
    finally:
        try:
            m.close_session()
        except Exception:
            try:
                if hasattr(m, 'transport') and hasattr(m.transport, 'close'):
                    m.transport.close()
            except Exception:
                pass


def disable(router_ip):
    # First, check the interface's current status.
    status_result = status(router_ip)
    if "is disabled" in status_result:
        return f"Cannot shutdown: Interface loopback {studentID} (checked by Netconf)"
    if "No Interface" in status_result:
        return f"Cannot shutdown: Interface loopback {studentID} (checked by Netconf)"

    m = get_manager(router_ip)
    try:
        netconf_config = f"""
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>Loopback{studentID}</name>
            <enabled>false</enabled>
        </interface>
    </interfaces>
</config>
"""

        # Using "merge" operation, which is the default.
        netconf_reply = netconf_edit_config(netconf_config, m)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface loopback {studentID} is shutdowned successfully using Netconf"
        else:
            return f"Cannot disable: Interface loopback {studentID}"
    except Exception as e:
        print(f"Error in disable: {e}")
        return f"Cannot disable: Interface loopback {studentID}"
    finally:
        try:
            m.close_session()
        except Exception:
            try:
                if hasattr(m, 'transport') and hasattr(m.transport, 'close'):
                    m.transport.close()
            except Exception:
                pass

def netconf_edit_config(netconf_config, m):
    return m.edit_config(target='running', config=netconf_config)


def status(router_ip):
    m = get_manager(router_ip)
    try:
        netconf_filter = f"""
<filter>
<interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
        <name>Loopback{studentID}</name>
    </interface>
</interfaces-state>
</filter>
"""

        # Use Netconf operational operation to get interfaces-state information
        netconf_reply = m.get(filter=netconf_filter)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

        # if there data return from netconf_reply_dict is not null, the operation-state of interface loopback is returned
        if ('rpc-reply' in netconf_reply_dict and 
            'data' in netconf_reply_dict['rpc-reply'] and 
            netconf_reply_dict['rpc-reply']['data'] and
            'interfaces-state' in netconf_reply_dict['rpc-reply']['data'] and
            'interface' in netconf_reply_dict['rpc-reply']['data']['interfaces-state']):
            # extract admin_status and oper_status from netconf_reply_dict
            interface_data = netconf_reply_dict['rpc-reply']['data']['interfaces-state']['interface']
            admin_status = interface_data['admin-status']
            oper_status = interface_data['oper-status']
            if admin_status == 'up':
                return f"Interface loopback {studentID} is enabled (checked by Netconf)"
            elif admin_status == 'down':
                return f"Interface loopback {studentID} is disabled (checked by Netconf)"
        else: # no operation-state data
            return f"No Interface loopback {studentID} (checked by Netconf)"
    except Exception as e:
       print(f"Error in status: {e}")
       return f"No Interface loopback {studentID} (checked by Netconf)"
    finally:
        try:
            m.close_session()
        except Exception:
            try:
                if hasattr(m, 'transport') and hasattr(m.transport, 'close'):
                    m.transport.close()
            except Exception:
                pass