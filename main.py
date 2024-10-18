from pynput import mouse, keyboard
import time
import threading

ms_events = 0
ms_cl_events = 0
kb_events = 0
print_interval = 0.1
lock = threading.Lock()
events_list = []


def on_move(x, y):
    global ms_events
    with lock:
        ms_events += 1


def on_click(x, y, button, pressed):
    global ms_cl_events
    with lock:
        ms_cl_events += 1


def on_scroll(x, y, dx, dy):
    global ms_cl_events
    with lock:
        ms_cl_events += 1


def on_press(key):
    global kb_events
    with lock:
        kb_events += 1


def on_release(key):
    global kb_events
    with lock:
        kb_events += 1


# 输出回报率
def print_counts():
    global ms_events, ms_cl_events, kb_events, events_list
    print("运行时间\t鼠标移动(最大)\t鼠标按键(最大)\t键盘(最大)")

    # 最大回报率
    ms_max = 0
    ms_cl_max = 0
    kb_max = 0
    # 下次输出时间
    next_time = time.perf_counter() + print_interval
    # 开始运行时间
    start_time = time.perf_counter()

    while True:
        with lock:
            # 统计前 (0.1 * 10) 秒的事件数
            events_list.append((ms_events, ms_cl_events, kb_events))
            if len(events_list) > 10:
                events_list.pop(0)

            ms_sum = sum(event[0] for event in events_list)
            ms_cl_sum = sum(event[1] for event in events_list)
            kb_sum = sum(event[2] for event in events_list)

            ms_max = max(ms_max, ms_sum)
            ms_cl_max = max(ms_cl_max, ms_cl_sum)
            kb_max = max(kb_max, kb_sum)

            # 距离开始运行时间
            elapsed_time = time.perf_counter() - start_time

            # 输出
            print(
                f"\r{' ' * 50}\r{elapsed_time:.3f}\t\t{ms_sum}({ms_max}){' ' * 5}\t{ms_cl_sum}({ms_cl_max}){' ' * 5}\t{kb_sum}({kb_max})",
                end="",
            )

            ms_events = 0
            ms_cl_events = 0
            kb_events = 0

        # 睡眠(带补正)
        next_time += print_interval
        sleep_time = next_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)


if __name__ == "__main__":

    mouse_listener = mouse.Listener(
        on_move=on_move, on_click=on_click, on_scroll=on_scroll
    )
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    print_thread = threading.Thread(target=print_counts, args=())
    print_thread.start()

    mouse_listener.join()
    keyboard_listener.join()
    print_thread.join()
