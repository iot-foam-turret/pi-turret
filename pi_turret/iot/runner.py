import threading
import time
from queue import Queue, Empty
from pi_turret.iot.turret.shadow_client import TurretShadowClient, map_state
from pi_turret.turret import Turret


def turret_thread_target(desired_state_queue: Queue, actual_state_queue: Queue):
    turret = Turret()
    # TODO: put calibrating state
    turret.calibrate()
    # TODO: put waiting state
    while True:
        try:
            state = desired_state_queue.get(block=False, timeout=0.1)
        except Empty:
            # Don't peg the CPU
            time.sleep(0.02)
            continue
        print(state)

        pitch = state["state"]["pitch"]
        yaw = state["state"]["yaw"]
        mode = state["state"]["mode"]
        control = state["state"]["control"]
        turret.move(pitch, yaw)
        new_state = map_state(
            pitch=turret.pitch,
            yaw=turret.yaw_motor,
            ammo=22, # TODO Update ammo count
            control=control,
            mode=mode
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
        desired_state_queue.put(payload)

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

    turret_thread = threading.Thread(target=turret_thread_target, args=(desired_state_queue, actual_state_queue), daemon=True)
    turret_thread.start()

    shadow_client_thread = threading.Thread(target=shadow_client_thread_target, args=(desired_state_queue, actual_state_queue), daemon=True)
    shadow_client_thread.start()

    # Not sure if we need the main thread to do anything
    while True:
        time.sleep(2)