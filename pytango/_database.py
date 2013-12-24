import PyTango

def create_component_device(device_name, component_name):
        db = PyTango.Database()
        dev_info = PyTango.DbDevInfo()
        dev_info._class = device_name
        dev_info.server = "component/" + component_name
        dev_info.name = "sys/component/" + component_name
        db.add_device(dev_info)

