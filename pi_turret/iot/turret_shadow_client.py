from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import argparse
import json


# Custom Shadow callback
def customShadowCallback_Delta(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    print(responseStatus)
    print(payload)
    payloadDict = json.loads(payload)
    print("++++++++DELTA++++++++++")
    print("pitch: " + str(payloadDict["state"]["pitch"]))
    print("yaw: " + str(payloadDict["state"]["yaw"]))
    print("version: " + str(payloadDict["version"]))
    print("+++++++++++++++++++++++\n\n")


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
# parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    # help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
connected = myAWSIoTMQTTShadowClient.connect()

print("Connected = " + str(connected))

# Create a deviceShadow with persistent subscription
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("Test", True)

# Custom MQTT message callback
def customCallback(payload, responseStatus, token):
    print("Payload Received: ")
    print(payload)
    print("--------------\n\n")

deviceShadowHandler.shadowGet(customCallback, 5)

def updateCallback(payload, responseStatus, token):
    print("Update finished")
    print(responseStatus)
    print(payload)

resetData = {
  "state": {
    "reported": {
      "pitch": 0,
      "yaw": 0
    }
  }
}

resetStr = json.dumps(resetData)

deviceShadowHandler.shadowUpdate(resetStr, updateCallback, 5)

# Listen on deltas
deviceShadowHandler.shadowRegisterDeltaCallback(customShadowCallback_Delta)

# Loop forever
while True:
    time.sleep(1)