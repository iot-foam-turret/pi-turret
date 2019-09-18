import threading
import time
import json
from queue import Queue, Empty
from pi_turret.iot.turret.shadow_client import TurretShadowClient, map_state
from pi_turret.iot.turret.control import Control
from pi_turret.turret import Turret, Mode
from pi_turret.test_scripts.combo_tracking import combo_tracking


def turret_thread_target(desired_state_queue: Queue, actual_state_queue: Queue):
    turret = Turret()
    # TODO: put calibrating state
    turret.calibrate()
    actual_state_queue.put(map_state(
        pitch=turret.pitch,
        yaw=turret.yaw,
        ammo=turret.ammo,
        mode=turret.mode
    ))
    auto_turret_thread = None
    stop_event = None
    def set_face_id_thread():
        stop_event = threading.Event()
        auto_turret_thread = threading.Thread(
            target=combo_tracking_target,
            args=(desired_state_queue, turret, stop_event),
            daemon=True
        )
        auto_turret_thread.start()
    set_face_id_thread()
    while True:
        try:
            state = desired_state_queue.get(block=True, timeout=0.1)
        except Empty:
            # Don't peg the CPU
            time.sleep(0.02)
            continue
        if state == "CLOSE":
            break
        state_dict = state.get("state")
        if state_dict is None:
            continue
        pitch = state_dict.get("pitch", turret.pitch)
        yaw = state_dict.get("yaw", turret.yaw)
        mode = state_dict.get("mode")
        control = state_dict.get("control")

        if mode == Control.faceId.value:
            if not auto_turret_thread:
                set_face_id_thread()
            continue

        if auto_turret_thread and not stop_event.is_set():
            # Close the thread
            stop_event.set()

        # Begin firing before movement so flywheel rev up time isn't wasted
        if mode == Mode.firing.value and turret.mode != Mode.firing and turret.mode != Mode.empty:
            def fire_callback():
                fire_complete_state = map_state(
                    pitch=turret.pitch,
                    yaw=turret.yaw,
                    ammo=turret.ammo,
                    control=Control[control],
                    mode=turret.mode
                )
                actual_state_queue.put(fire_complete_state)

            turret.burst_fire(0.5, fire_callback)

        turret.move(pitch, yaw)
        new_state = map_state(
            pitch=turret.pitch,
            yaw=turret.yaw,
            ammo=turret.ammo,
            control=Control[control],
            mode=turret.mode
        )
        actual_state_queue.put(new_state)


def combo_tracking_target(desired_state_queue: Queue, turret: Turret, stop_event):
    """
    combo_tracking_target
    """
    def callback(face_x, face_y):
        # TODO Map
        pitch = turret.pitch + face_y
        yaw = turret.yaw + face_x
        new_state = map_state(
            pitch=pitch,
            yaw=yaw,
            control=Control.faceId,
            mode=Mode.firing
        )
        desired_state_queue.put(new_state)
    combo_tracking(stop_event, callback=callback)


def shadow_client_thread_target(desired_state_queue: Queue, actual_state_queue: Queue):
    shadow_client = TurretShadowClient()

    def shadow_updated(payload, responseStatus, token):
        print("Payload Reported: ")
        print(payload)
        print("--------------\n")

    def shadow_delta_callback(payload, responseStatus, token):
        print("Payload Received: ")
        print(payload)
        print("--------------\n")
        payloadDictionary = json.loads(payload)
        desired_state_queue.put(payloadDictionary, block=False)

    def connect_shadow(payload, responseStatus, token):
        print("Shadow Reset: ")
        print(payload)
        print("--------------\n")
        shadow_client.subscribe(shadow_delta_callback)

        while True:
            try:
                state = actual_state_queue.get(block=False, timeout=0.1)
            except Empty:
                # Don't peg the CPU
                time.sleep(0.02)
                continue
            shadow_client.update_shadow(state, shadow_updated)

    shadow_client.reset_shadow(connect_shadow)


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
