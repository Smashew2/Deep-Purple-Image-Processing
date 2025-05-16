import tkinter as tk
from tkinter import ttk
import time
import threading
import subprocess
import os
import serial

# Flags
loading_active = False
paused = False
showing_processing = False
runorder_process = None

def set_pause_flag(value: bool):
    try:
        with open("/home/asmluser/ImageStorage/pause_flag.txt", "w") as file:
            file.write("1" if value else "0")
    except Exception as e:
        print(f"Error setting pause flag: {e}")

def show_hole_input_screen():
    for widget in root.winfo_children():
        widget.destroy()

    title_label = tk.Label(root, text="Retake Specific Hole", font=("Helvetica", 16))
    title_label.pack(pady=10)

    instruction_label = tk.Label(root, text="Enter Hole Code (e.g., A0170):")
    instruction_label.pack(pady=5)

    hole_entry = tk.Entry(root, width=10)
    hole_entry.pack(pady=5)

    def send_hole_command():
        hole_code = hole_entry.get().strip().upper()
        if len(hole_code) == 5:
            try:
                ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
                time.sleep(2)
                ser.write((hole_code + "\\n").encode())
                ser.flush()
                print(f"Sent command to Arduino: {hole_code}")

                # Wait for signal from Arduino
                print("Waiting for Arduino ready signal...")
                while True:
                    if ser.in_waiting > 0:
                        response = ser.readline().decode('utf-8').strip()
                        if response == '1':
                            print("Arduino ready for retake.")
                            break
                ser.close()

                # Run the capture script
                subprocess.run(["python3", "/home/asmluser/guvcviewCameraControl"], check=True)
                tk.messagebox.showinfo("Success", f"Retake of {hole_code} complete.")
            except Exception as e:
                print(f"Error during retake: {e}")
                tk.messagebox.showerror("Error", f"Failed to retake: {e}")
        else:
            tk.messagebox.showerror("Input Error", "Hole code must be exactly 5 characters.")

    send_button = tk.Button(root, text="Send & Retake", command=send_hole_command)
    send_button.pack(pady=10)

    back_button = tk.Button(root, text="Back", command=show_main_screen)
    back_button.pack(pady=5)


def show_main_screen():
    for widget in root.winfo_children():
        widget.destroy()
    root.title("Automatic Tin Detection")
    global progress_label, progress_bar
    global start_button, stop_button, reset_button
    global showing_processing
    showing_processing = False
    progress_label = tk.Label(root, text="Image Taking: 0%")
    progress_label.pack(pady=(10, 0))
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode='determinate')
    progress_bar.pack(pady=10)
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    start_button = tk.Button(button_frame, text="Start", command=start_loading)
    start_button.grid(row=0, column=0, padx=5)
    stop_button = tk.Button(button_frame, text="Stop", command=stop_continue_loading, state=tk.DISABLED)
    stop_button.grid(row=0, column=1, padx=5)
    reset_button = tk.Button(button_frame, text="Reset", command=reset_loading, state=tk.DISABLED)
    reset_button.grid(row=0, column=2, padx=5)
    goto_button = tk.Button(root, text="Go to Hole", command=show_hole_input_screen)
    goto_button.pack(pady=5)

def read_run_count():
    try:
        with open("/home/asmluser/ImageStorage/run_count.txt", "r") as file:
            return int(file.read().strip())
    except:
        return 0

def read_image_processing_counter():
    try:
        with open("/home/asmluser/ImageStorage/image_counter.txt", "r") as file:
            return int(file.read().strip())
    except:
        return 0

def update_progress_bar():
    max_count = 1587
    global showing_processing
    if not showing_processing:
        run_count = read_run_count()
        percent = (run_count / max_count) * 100
        progress_bar['value'] = percent
        progress_label.config(text=f"Image Taking: {int(percent)}%")
        if run_count >= max_count:
            showing_processing = True
            progress_label.config(text="Image Processing: 0%")
            progress_bar['value'] = 0
    else:
        image_counter = read_image_processing_counter()
        percent = (image_counter / max_count) * 100
        progress_bar['value'] = percent
        progress_label.config(text=f"Image Processing: {int(percent)}%")
        if image_counter >= max_count:
            progress_label.config(text="Image Processing Complete!")
            stop_button.config(state=tk.DISABLED)
            reset_button.config(state=tk.NORMAL)

def update_progress_periodically():
    while loading_active:
        if not paused:
            update_progress_bar()
        time.sleep(1)
        root.update_idletasks()

def start_loading():
    global loading_active, paused, runorder_process
    loading_active = True
    paused = False
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL, text="Stop")
    reset_button.config(state=tk.DISABLED)
    set_pause_flag(False)
    try:
        runorder_process = subprocess.Popen(["python3", "/home/asmluser/RunOrder"])
    except Exception as e:
        print(f"Failed to launch RunOrder: {e}")
    threading.Thread(target=update_progress_periodically, daemon=True).start()

def stop_continue_loading():
    global paused
    if paused:
        paused = False
        stop_button.config(text="Stop")
        reset_button.config(state=tk.DISABLED)
        set_pause_flag(False)
    else:
        paused = True
        stop_button.config(text="Continue")
        reset_button.config(state=tk.NORMAL)
        set_pause_flag(True)

def reset_loading():
    global loading_active, paused, showing_processing, runorder_process
    loading_active = False
    paused = False
    showing_processing = False
    set_pause_flag(False)
    if runorder_process:
        runorder_process.terminate()
        runorder_process = None
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)
        ser.write(b'RR000')
        ser.flush()
        time.sleep(2)
        
                
        data = ser.readline().decode('utf-8').strip() #Read data in
        print(f"Data recieved: {data}")
        ser.close()
    except Exception as e:
        print(f"Error sending RESET to Arduino: {e}")
    try:
        image_folder = "/home/asmluser/ImageStorage"
        for filename in os.listdir(image_folder):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                os.remove(os.path.join(image_folder, filename))
        with open(os.path.join(image_folder, "run_count.txt"), "w") as f:
            f.write("0")
        with open(os.path.join(image_folder, "image_counter.txt"), "w") as f:
            f.write("0")
    except Exception as e:
        print(f"Error during reset: {e}")
    

def on_gui_close():
    global runorder_process
    try:
        with open("/home/asmluser/ImageStorage/image_counter.txt", "w") as file:
            file.write("0")
    except:
        pass
    set_pause_flag(False)
    if runorder_process:
        runorder_process.terminate()
        runorder_process = None
    root.destroy()

root = tk.Tk()
root.title("Automatic Tin Detection")
root.geometry("350x400")
show_main_screen()
root.protocol("WM_DELETE_WINDOW", on_gui_close)
root.mainloop()
