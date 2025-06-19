import tkinter as tk
from tkinter import ttk, messagebox
import math
import sounddevice as sd
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.base_noise_level = None
        self.calibrating = False
        self.auto_mode = False
        self.running = True
        self.calibration_samples = []
        self.setup_ui()
        self.setup_audio()
        self.setup_microphone()

    def setup_ui(self):
        self.root.title("🎚️ Авторегулятор громкости")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#2c3e50")
        style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 10), padding=8, background="#3498db", foreground="white")
        style.map("TButton", background=[("active", "#2980b9"), ("pressed", "#2c3e50")], foreground=[("active", "white"), ("pressed", "white")])
        style.configure("Horizontal.TScale", background="#3498db", troughcolor="#34495e")
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        header = ttk.Label(main_frame, text="АВТОРЕГУЛЯТОР ГРОМКОСТИ", font=("Helvetica", 14, "bold"))
        header.pack(pady=(0, 15))
        
        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(fill="x", pady=5)
        self.volume_label = ttk.Label(volume_frame, text="Громкость: 0%", font=("Helvetica", 12, "bold"))
        self.volume_label.pack(anchor="w")
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=100, style="Horizontal.TScale", command=self.on_volume_change)
        self.volume_slider.pack(fill="x", pady=5)
        
        noise_frame = ttk.Frame(main_frame)
        noise_frame.pack(fill="x", pady=10)
        self.noise_label = ttk.Label(noise_frame, text="Уровень шума: -- dB (база: -- dB)")
        self.noise_label.pack(anchor="w")
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        self.mute_btn = ttk.Button(btn_frame, text="🔇 Mute", width=10, command=self.toggle_mute)
        self.mute_btn.grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="🔊 +10%", width=10, command=lambda: self.adjust_volume(10)).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="🔉 -10%", width=10, command=lambda: self.adjust_volume(-10)).grid(row=0, column=2, padx=5)
        
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(pady=10)
        self.calibrate_btn = ttk.Button(mode_frame, text="📏 Калибровка", width=15, command=self.start_calibration)
        self.calibrate_btn.grid(row=0, column=0, padx=5)
        self.auto_btn = ttk.Button(mode_frame, text="🤖 Авто ВКЛ", width=15, command=self.toggle_auto)
        self.auto_btn.grid(row=0, column=1, padx=5)

    def setup_audio(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            current_vol = self.volume_interface.GetMasterVolumeLevelScalar()
            self.volume_slider.set(math.floor(current_vol * 100))
            self.update_volume_label()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к аудиоустройству:\n{str(e)}")
            self.volume_label.config(text="Ошибка аудио")
            self.volume_slider.config(state="disabled")
            self.mute_btn.config(state="disabled")

    def setup_microphone(self):
        try:
            self.current_rms = 0
            self.stream = sd.InputStream(samplerate=44100, channels=1, dtype="float32", callback=self.audio_callback)
            self.stream.start()
            self.check_noise_level()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к микрофону:\n{str(e)}")
            self.noise_label.config(text="Микрофон не обнаружен")

    def audio_callback(self, indata, frames, time, status):
        self.current_rms = np.sqrt(np.mean(indata**2))
        if self.calibrating:
            self.calibration_samples.append(self.current_rms)

    def start_calibration(self):
        if not self.calibrating:
            self.calibration_samples = []
            self.calibrating = True
            self.calibrate_btn.config(text="📏 Калибруется...")
            self.root.after(3000, self.finish_calibration)
        else:
            messagebox.showinfo("Информация", "Калибровка уже выполняется")

    def finish_calibration(self):
        if len(self.calibration_samples) > 0:
            avg_rms = np.mean(self.calibration_samples)
            self.base_noise_level = 20 * np.log10(avg_rms) if avg_rms > 0 else -60
            self.update_noise_level_display()
        self.calibrating = False
        self.calibrate_btn.config(text="📏 Калибровка")

    def check_noise_level(self):
        if hasattr(self, "current_rms"):
            try:
                db = 20 * np.log10(self.current_rms) if self.current_rms > 0 else -60
                if self.auto_mode and self.base_noise_level is not None:
                    current_vol = int(self.volume_slider.get())
                    if db > self.base_noise_level + 3:
                        new_vol = max(0, current_vol - 5)
                    elif db < self.base_noise_level - 3:
                        new_vol = min(100, current_vol + 5)
                    else:
                        new_vol = current_vol
                    if new_vol != current_vol:
                        self.set_volume(new_vol)
                        self.volume_slider.set(new_vol)
                        self.update_volume_label()
                self.update_noise_level_display(db)
            except Exception as e:
                print(f"Ошибка обработки звука: {e}")
        if self.running:
            self.root.after(100, self.check_noise_level)

    def update_noise_level_display(self, current_db=None):
        if current_db is None:
            current_db = 20 * np.log10(self.current_rms) if hasattr(self, "current_rms") and self.current_rms > 0 else -60
        base_text = f"{self.base_noise_level:.1f} dB" if self.base_noise_level is not None else "-- dB"
        self.noise_label.config(text=f"Уровень шума: {current_db:.1f} dB (база: {base_text})")

    def toggle_auto(self):
        if self.base_noise_level is None:
            messagebox.showwarning("Внимание", "Сначала выполните калибровку!")
            return
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.auto_btn.config(text="🤖 Авто ВЫКЛ")
        else:
            self.auto_btn.config(text="🤖 Авто ВКЛ")

    def on_volume_change(self, val):
        self.set_volume(int(float(val)))
        self.update_volume_label()

    def set_volume(self, volume):
        if 0 <= volume <= 100:
            self.volume_interface.SetMasterVolumeLevelScalar(volume/100, None)

    def toggle_mute(self):
        is_muted = self.volume_interface.GetMute()
        self.volume_interface.SetMute(not is_muted, None)
        self.mute_btn.config(text="🔈 Unmute" if not is_muted else "🔇 Mute")

    def adjust_volume(self, delta):
        new_vol = max(0, min(100, int(self.volume_slider.get()) + delta))
        self.volume_slider.set(new_vol)
        self.set_volume(new_vol)
        self.update_volume_label()

    def update_volume_label(self):
        self.volume_label.config(text=f"Громкость: {int(self.volume_slider.get())}%")

    def on_closing(self):
        self.running = False
        if hasattr(self, "stream"):
            self.stream.stop()
            self.stream.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VolumeControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
