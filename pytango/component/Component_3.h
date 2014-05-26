#ifndef Component_3_H
#define Component_3_H

#include <tango.h>



namespace Component_3_ns
{

class Component_3 : public TANGO_BASE_CLASS
{

private:
	bool attr_c_state;
	Tango::DeviceProxy *c1_dev;
	Tango::DeviceProxy *c2_dev;

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
	virtual void pa();
	virtual bool is_PA_allowed(const CORBA::Any &any);


};

}	//	End of namespace

#endif   //	Component_3_H
