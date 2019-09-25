import threading
import time
import json
from queue import Queue, Empty
from pi_turret.iot.turret.shadow_client import TurretShadowClient, map_state
from pi_turret.iot.turret.control import Control
from pi_turret.turret import Turret, Mode
from pi_turret.test_scripts.combo_tracking import combo_tracking


def turret_thread_target(desired_state_queue: Queue, actual_state_queue: Queue, stop_turret_event: threading.Event):
    turret = Turret()
    # turret.calibrate()
    desired_state_queue.put(
        {
            "state": map_state(
                pitch=turret.pitch,
                yaw=turret.yaw,
                ammo=turret.ammo,
                mode=turret.mode
            )
        }
    )
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
        return (auto_turret_thread, stop_event)
    # auto_turret_thread, stop_event = set_face_id_thread()
    startup_time = time.time()
    while True:
        if stop_turret_event.is_set():
            break
        try:
            state = desired_state_queue.get(block=True, timeout=0.1)
        except Empty:
            # Don't peg the CPU
            time.sleep(0.02)
            continue
        state_dict = state.get("state")
        if state_dict is None:
            continue
        pitch = state_dict.get("pitch", turret.pitch)
        yaw = state_dict.get("yaw", turret.yaw)
        mode = state_dict.get("mode")
        control = state_dict.get("control")

        # If switching to faceId start thread thread
        if control == Control.faceId.value and not auto_turret_thread:
            auto_turret_thread, stop_event = set_face_id_thread()

        # If switching to manual stop faceId thread
        if control == Control.manual.value and auto_turret_thread and not stop_event.is_set():
            # Close the thread
            stop_event.set()
            auto_turret_thread = None

        # Begin firing before movement so flywheel rev up time isn't wasted
        if mode == Mode.firing.value and turret.mode != Mode.firing and turret.mode != Mode.empty:
            def fire_callback():
                fire_complete_state = map_state(
                    pitch=turret.pitch,
                    yaw=turret.yaw,
                    ammo=turret.ammo,
                    control=Control(control),
                    mode=turret.mode
                )
                actual_state_queue.put(fire_complete_state)

            turret.burst_fire(0.5, fire_callback)
        print(f"Moving to {pitch}, {yaw} seconds {time.time() - startup_time}")
        turret.move(pitch, yaw)
        new_state = map_state(
            pitch=turret.pitch,
            yaw=turret.yaw,
            ammo=turret.ammo,
            control=Control(control),
            mode=turret.mode
        )
        actual_state_queue.put(new_state)

    #Cleanup (Not sure why this isn't happening without explicit calls)
    turret.yaw_motor.motor.release()
    turret.pitch_motor.motor.release()

def combo_tracking_target(desired_state_queue: Queue, turret: Turret, stop_event):
    """
    combo_tracking_target
    """
    def update_turret_callback(face_x=None, face_y=None, fire=False):
        # Camera x to view angle
        # y = 0.0421875x -27

        # Camera y to view angle
        # y = -0.05694444444x + 20.5
        if face_x is not None and face_y is not None:
            pitch = -0.05694444444 * face_y + 20.5 - turret.pitch
            yaw = -0.0421875 * face_x + 27 - turret.yaw
        else:
            pitch = turret.pitch
            yaw = turret.yaw
        new_state = map_state(
            pitch=pitch,
            yaw=-yaw,
            control=Control.faceId,
            mode=Mode.firing if fire else Mode.waiting
        )
        desired_state_queue.put({
            "state": new_state
        })

    combo_tracking(stop_event, callback=update_turret_callback, show_ui=True)


def shadow_client_thread_target(desired_state_queue: Queue, actual_state_queue: Queue, stop_event: threading.Event):
    shadow_client = TurretShadowClient()

    def shadow_updated(payload, responseStatus, token):
        # print("Payload Reported: ")
        # print(payload)
        # print("--------------\n")
        pass

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
            if stop_event.is_set():
                break
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
    close_event = threading.Event()

    turret_thread = threading.Thread(target=turret_thread_target, args=(
        desired_state_queue, actual_state_queue, close_event), daemon=True)
    turret_thread.start()

    shadow_client_thread = threading.Thread(target=shadow_client_thread_target, args=(
        desired_state_queue, actual_state_queue, close_event), daemon=True)
    shadow_client_thread.start()

    # Not sure if we need the main thread to do anything
    try:
        while True:
            time.sleep(2)
    except:
        print("Closing")
        close_event.set()
        time.sleep(2)
