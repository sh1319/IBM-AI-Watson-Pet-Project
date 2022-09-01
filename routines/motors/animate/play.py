import time

def animate(left_arm, right_arm, delay=0.5):
    while True:
        left_arm.max()
        right_arm.min()
        time.sleep(delay)
        left_arm.mid()
        right_arm.mid()
        time.sleep(delay)
        left_arm.max()
        right_arm.min()
        time.sleep(delay)
        