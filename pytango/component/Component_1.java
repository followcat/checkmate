package pytango.component;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;
import org.tango.DeviceState;
import org.tango.server.InvocationContext;
import org.tango.server.ServerManager;
import org.tango.server.annotation.AroundInvoke;
import org.tango.server.annotation.Attribute;
import org.tango.server.annotation.AttributeProperties;
import org.tango.server.annotation.ClassProperty;
import org.tango.server.annotation.Command;
import org.tango.server.annotation.Delete;
import org.tango.server.annotation.Device;
import org.tango.server.annotation.DeviceProperty;
import org.tango.server.annotation.DeviceManagement;
import org.tango.server.annotation.DynamicManagement;
import org.tango.server.annotation.Init;
import org.tango.server.annotation.State;
import org.tango.server.annotation.StateMachine;
import org.tango.server.annotation.Status;
import org.tango.server.attribute.AttributeValue;
import org.tango.server.device.DeviceManager;
import org.tango.server.dynamic.DynamicManager;
import org.tango.server.events.EventType;
import org.tango.utils.DevFailedUtils;

import fr.esrf.Tango.*;
import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.TangoApi.DeviceData;

@Device
public class Component_1 {

    private static final Logger logger = LoggerFactory.getLogger(Component_1.class);
    private static final XLogger xlogger = XLoggerFactory.getXLogger(Component_1.class);
    private DeviceProxy c2_dev;
    private DeviceProxy c3_dev;

    @Init(lazyLoading = false)
    public final void initDevice() throws DevFailed {
        xlogger.entry();
        logger.debug("init");
        c2_dev = new DeviceProxy("sys/component_2/C2");
        c3_dev = new DeviceProxy("sys/component_3/C3");
        
        xlogger.exit();
    }

    @Delete
    public final void deleteDevice() throws DevFailed {
        xlogger.entry();
        xlogger.exit();
    }

    @AroundInvoke
    public final void aroundInvoke(final InvocationContext ctx) throws DevFailed {
        xlogger.entry(ctx);
        xlogger.exit();
    }
    
    @DynamicManagement
    private DynamicManager dynamicManager;
    public void setDynamicManager(final DynamicManager dynamicManager) {
        this.dynamicManager = dynamicManager;
    }

    @State
    private DevState state = DevState.UNKNOWN;

    public final DevState getState() throws DevFailed {
        return state;
    }

    public void setState(final DevState state) {
        this.state = state;
    }
    
    @Status
    private String status = "Server is starting. The device state is unknown";

    public final String getStatus() throws DevFailed {
        return status;
    }

    public void setStatus(final String status) {
        this.status = status;
    }
    
    public void sleep() {
        try{
            Thread.sleep(100);
        }
        catch (InterruptedException e) {}
    }
    
    private static Boolean c_state = true;

    @DeviceManagement
    DeviceManager deviceManager;

    public void setDeviceManager(final DeviceManager deviceManager) {
        this.deviceManager = deviceManager;
    }

	@Attribute(name="PA", pushDataReady = true)
	private int pA = 1;

	public int getPA() {
		return pA;
	}

    @Command(name="AC", inTypeDesc="param", outTypeDesc="")
    public void AC(String[] param) throws DevFailed {
        xlogger.entry();
        if (c_state == true) {
            toggle();
            c3_dev.command_inout("RE");
            c2_dev.command_inout("ARE");
        }
        xlogger.exit();
    }
    
    @Command(name="AP", inTypeDesc="param", outTypeDesc="")
    public void AP(String[] param) throws DevFailed {
        xlogger.entry();
        c2_dev.command_inout("DA");
        xlogger.exit();
    }
    
    @Command(name="PP", inTypeDesc="param", outTypeDesc="")
    public void PP(String[] param) throws DevFailed {
        xlogger.entry();
        if (c_state == false) {
            toggle();
            pA++;
            deviceManager.pushDataReadyEvent("PA", pA);
        }
        xlogger.exit();
    }
    
    private void toggle(){
           c_state = !c_state;
    }
    
    public static void main(final String[] args) {
        ServerManager.getInstance().start(args, Component_1.class);
        System.out.println("------- Started -------------");
    }
}
