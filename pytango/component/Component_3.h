#ifndef Component_3_H
#define Component_3_H

#include <tango.h>



namespace Component_3_ns
{

class PA_callback : public Tango::CallBack
{
	public:
		PA_callback(Tango::DeviceImpl *c3) : CallBack()
		{device = c3;};
		~PA_callback() {};

	private:
		Tango::DeviceImpl *device;

	public:
		virtual void push_event(Tango::DataReadyEventData *event);
};


class Component_3 : public TANGO_BASE_CLASS
{

private:
	bool attr_c_state;
	Tango::DeviceProxy *c1_dev;
	Tango::DeviceProxy *c2_dev;
    PA_callback *pa_callback;

public:
	Component_3(Tango::DeviceClass *cl,string &s);
	Component_3(Tango::DeviceClass *cl,const char *s);
	Component_3(Tango::DeviceClass *cl,const char *s,const char *d);
	~Component_3() {delete_device();};

//	Miscellaneous methods
public:
	void delete_device();
	virtual void init_device();
	virtual void always_executed_hook();

//	Attribute methods
public:
	virtual void read_attr_hardware(vector<long> &attr_list);
	void add_dynamic_attributes();

public:
	virtual void toggle();
	virtual bool is_toggle_allowed(const CORBA::Any &any);
	virtual void re();
	virtual bool is_RE_allowed(const CORBA::Any &any);
	virtual void rl();
	virtual bool is_RL_allowed(const CORBA::Any &any);
    void pa(Tango::DataReadyEventData *event);


};

}	//	End of namespace

#endif   //	Component_3_H
