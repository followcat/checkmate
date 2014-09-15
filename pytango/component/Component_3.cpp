static const char *RcsId = "$Id:  $";

#include <Component_3.h>
#include <Component_3Class.h>


namespace Component_3_ns
{
void PA_callback::push_event(Tango::DataReadyEventData *event)
{
	 (static_cast<Component_3 *>(device))->pa(event);
	
}


Component_3::Component_3(Tango::DeviceClass *cl, string &s)
 : TANGO_BASE_CLASS(cl, s.c_str())
{
	init_device();
	
}

Component_3::Component_3(Tango::DeviceClass *cl, const char *s)
 : TANGO_BASE_CLASS(cl, s)
{
	init_device();
	
}

Component_3::Component_3(Tango::DeviceClass *cl, const char *s, const char *d)
 : TANGO_BASE_CLASS(cl, s, d)
{
	init_device();

}


void Component_3::delete_device()
{
	DEBUG_STREAM << "Component_3::delete_device() " << device_name << endl;
}


void Component_3::init_device()
{
	DEBUG_STREAM << "Component_3::init_device() create device " << device_name << endl;

	set_state(Tango::ON);
	attr_c_state = false;
	c1_dev = new Tango::DeviceProxy("sys/component_1/C1");
	c2_dev = new Tango::DeviceProxy("sys/component_2/C2");
    pa_callback = new PA_callback(this);
}


void Component_3::always_executed_hook()
{
	INFO_STREAM << "Component_3::always_executed_hook()  " << device_name << endl;
	c1_dev->subscribe_event("PA", Tango::DATA_READY_EVENT, static_cast<Tango::CallBack *>(pa_callback));
}

//--------------------------------------------------------
/**
 *	Method      : Component_3::read_attr_hardware()
 *	Description : Hardware acquisition for attributes
 */
//--------------------------------------------------------
void Component_3::read_attr_hardware(TANGO_UNUSED(vector<long> &attr_list))
{
	DEBUG_STREAM << "Component_3::read_attr_hardware(vector<long> &attr_list) entering... " << endl;

}


void Component_3::add_dynamic_attributes()
{

}


void Component_3::toggle()
{
	DEBUG_STREAM << "Component_3::toggle()  - " << device_name << endl;
	attr_c_state = not attr_c_state;
}

void Component_3::re()
{
	DEBUG_STREAM << "Component_3::RE()  - " << device_name << endl;
	if(attr_c_state == false)
	{
		toggle();
	}
}

void Component_3::rl()
{
	DEBUG_STREAM << "Component_3::RL()  - " << device_name << endl;
	if(attr_c_state == true)
	{
		toggle();
		c2_dev->command_inout("dr");
	}
}

void Component_3::pa(Tango::DataReadyEventData *event)
{
	DEBUG_STREAM << "Component_3::pa()  - " << device_name << endl;
	attr_c_state = false;
}

} //	namespace
