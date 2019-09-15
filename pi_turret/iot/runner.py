import threading
import time
import json
from queue import Queue, Empty
from pi_turret.iot.turret.shadow_client import TurretShadowClient, map_state
from pi_turret.turret import Turret, Mode


def turret_thread_target(desired_state_queue: Queue, actual_state_queue: Queue):
    turret = Turret()
    # TODO: put calibrating state
    turret.calibrate()
    actual_state_queue.put(map_state(
        pitch=turret.pitch,
        yaw=turret.yaw,
        ammo=turret.ammo,
        control=control,
        mode=turret.mode
    ))
    # TODO: put waiting state
    while True:
        try:
            state = desired_state_queue.get(block=True, timeout=0.1)
        except Empty:
            # Don't peg the CPU
            time.sleep(0.02)
            continue
        print(state)
        if state == "CLOSE":
            break
        stateDict = state.get("state")
        if stateDict is None:
            continue
        pitch = stateDict.get("pitch", turret.pitch)
        yaw = stateDict.get("yaw", turret.yaw)
        mode = stateDict.get("mode")
        control = stateDict.get("control")

        # Begin firing before movement so flywheel rev up time isn't wasted
        if mode is Mode.firing.value and turret.mode is not Mode.firing and turret.mode is not Mode.empty:
            def fire_callback():
                fire_complete_state = map_state(
                    pitch=turret.pitch,
                    yaw=turret.yaw,
                    ammo=turret.ammo,
                    control=control,
                    mode=turret.mode.value
                )
                actual_state_queue.put(fire_complete_state)

            turret.burst_fire(0.5, fire_callback)

        turret.move(pitch, yaw)
        new_state = map_state(
            pitch=turret.pitch,
            yaw=turret.yaw,
            ammo=turret.ammo,
            control=control,
            mode=turret.mode.value
        )
        actual_state_queue.put(new_state)


def shadow_client_thread_target(desired_state_queue: Queue, actual_state_queue: Queue):
    shadow_client = TurretShadowClient()

    def shadow_updated(payload, responseStatus, token):
        print("Payload Reported: ")
        print(payload)
        print("--------------\n\n")

    def shadow_delta_callback(payload, responseStatus, token):
        print("Payload Received: ")
        payloadDictionary = json.loads(payload)
        desired_state_queue.put(payloadDictionary, block=False)

    shadow_client.subscribe(shadow_delta_callback)

    while True:
        try:
            state = actual_state_queue.get(block=False, timeout=0.1)
        except Empty:
            # Don't peg the CPU
            time.sleep(0.02)
            continue
        print(state)
        shadow_client.update_shadow(state, shadow_updated)


def main():
    desired_state_queue = Queue()
    actual_state_queue = Queue()

    turret_thread = threading.Thread(target=turret_thread_target, args=(
        desired_state_queue, actual_state_queue), daemon=True)
    turret_thread.start()

    shadow_client_thread = threading.Thread(target=shadow_client_thread_target, args=(
        desired_state_queue, actual_state_queue), daemon=True)
    shadow_client_thread.start()

    # Not sure if we need the main thread to do anything
    try:
        while True:
            time.sleep(2)
    except:
        print("Closing")
        desired_state_queue.put("CLOSE", block=False)
        time.sleep(2)
