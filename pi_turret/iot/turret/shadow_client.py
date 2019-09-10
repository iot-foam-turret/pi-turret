from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json
from pi_turret.iot.turret.control import Control
from pi_turret.iot.turret.mode import Mode


def map_state(pitch: float, yaw: float, ammo: int, control: Control = Control.manual, mode: Mode = Mode.waiting):
    return {
        "pitch": pitch,
        "yaw": yaw,
        "ammo": ammo,
        "control": control.value if control is not None else Control.manual.value,
        "mode": mode.value if mode is not None else Mode.waiting.value
    }


class TurretShadowClient:
    """
    Thin wrapper around AWSIoTMQTTShadowClient.
    """

    def __init__(
        self,
        clientId="Pi-Turret",
        host="a1ele7j1b00m5f-ats.iot.us-west-2.amazonaws.com",
        rootCAPath="pi_turret/iot/.device_cert/root-CA.crt",
        privateKeyPath="pi_turret/iot/.device_cert/91fe20c098-private.pem.key",
        certificatePath="pi_turret/iot/.device_cert/91fe20c098-certificate.pem.crt"
    ):
        shadowClient = AWSIoTMQTTShadowClient(clientId)
        shadowClient.configureEndpoint(host, 8883)
        shadowClient.configureCredentials(
            rootCAPath, privateKeyPath, certificatePath)

        # AWSIoTMQTTShadowClient configuration
        shadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
        shadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
        shadowClient.configureMQTTOperationTimeout(5)  # 5 sec
        shadowClient.connect()
        self.shadowClient = shadowClient

        deviceShadowHandler = shadowClient.createShadowHandlerWithName(
            clientId, True)
        self.shadowHandler = deviceShadowHandler

    def get_shadow(self, callback):
        self.shadowHandler.shadowGet(callback, 5)

    def update_shadow(self, state, callback):
        data = {
            "state": {
                "reported": state
            }
        }

        payload = json.dumps(data)

        self.shadowHandler.shadowUpdate(payload, callback, 5)

    def subscribe(self, callback):
        """
        Custom Shadow callback
        def customShadowCallback_Delta(payload, responseStatus, token):
            # payload is a JSON string ready to be parsed using json.loads(...)
            print(responseStatus)
            print(payload)
            payloadDict = json.loads(payload)
            print("++++++++DELTA++++++++++")
            print("pitch: " + str(payloadDict["state"]["pitch"]))
            print("yaw: " + str(payloadDict["state"]["yaw"]))
            print("version: " + str(payloadDict["version"]))
            print("+++++++++++++++++++++++\n\n")
        """
        self.shadowHandler.shadowRegisterDeltaCallback(callback)


if __name__ == "__main__":
    from pi_turret.iot.turret.control import Control
    from pi_turret.iot.turret.mode import Mode
    CLIENT = TurretShadowClient()

    def customCallback(payload, responseStatus, token):
        print("Payload Received: ")
        print(payload)
        print("--------------\n\n")
    CLIENT.get_shadow(customCallback)

    NEW_STATE = map_state(0, 0, 22, Control.manual, Mode.waiting)
    CLIENT.update_shadow(NEW_STATE, customCallback)
    CLIENT.subscribe(customCallback)
    # Loop forever
    while True:
        time.sleep(1)
