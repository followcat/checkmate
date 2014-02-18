static const char *RcsId = "$Id:  $";

#include <tango.h>
#include <Component_3Class.h>

void Tango::DServer::class_factory()
{
	add_class(Component_3_ns::Component_3Class::init("Component_3"));
}
