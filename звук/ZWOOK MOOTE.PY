import tkinter as tk
from tkinter import ttk, messagebox
import math
import sys
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.setup_audio()
        
    def setup_ui(self):
        self.root.title("Системный регулятор громкости")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Стиль для кнопок
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 12))
        
        # Основные элементы
        self.volume_label = ttk.Label(self.root, text="Загрузка...")
        self.volume_label.pack(pady=10)
        
        self.volume_slider = ttk.Scale(
            self.root, from_=0, to=100, 
            orient="horizontal", command=self.on_volume_change
        )
        self.volume_slider.pack(fill='x', padx=20, pady=5)
        
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.mute_btn = ttk.Button(
            btn_frame, text="Mute", width=8, 
            command=self.toggle_mute
        )
        self.mute_btn.pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, text="+10%", width=8,
            command=lambda: self.adjust_volume(10)
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, text="-10%", width=8,
            command=lambda: self.adjust_volume(-10)
        ).pack(side='left', padx=5)
        
    def setup_audio(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            
            # Установка начальных значений
            current_vol = self.volume_interface.GetMasterVolumeLevelScalar()
            self.volume_slider.set(math.floor(current_vol * 100))
            self.update_volume_label()
            
        except Exception as e:
            messagebox.showerror(
                "Ошибка", 
                f"Не удалось инициализировать аудио систему:\n{str(e)}"
            )
            self.volume_label.config(text="Аудио система недоступна")
            self.volume_slider.config(state='disabled')
            self.mute_btn.config(state='disabled')
    
    def on_volume_change(self, val):
        volume = int(float(val))
        self.set_volume(volume)
        self.update_volume_label()
    
    def set_volume(self, volume):
        if 0 <= volume <= 100:
            vol_scalar = volume / 100
            self.volume_interface.SetMasterVolumeLevelScalar(vol_scalar, None)
    
    def toggle_mute(self):
        is_muted = self.volume_interface.GetMute()
        self.volume_interface.SetMute(not is_muted, None)
        self.mute_btn.config(text="Unmute" if not is_muted else "Mute")
    
    def adjust_volume(self, delta):
        current = int(self.volume_slider.get())
        new_vol = max(0, min(100, current + delta))
        self.volume_slider.set(new_vol)
        self.set_volume(new_vol)
        self.update_volume_label()
    
    def update_volume_label(self):
        current_vol = int(self.volume_slider.get())
        self.volume_label.config(text=f"Текущая громкость: {current_vol}%")
        
        # Визуальная индикация
        if current_vol == 0:
            self.volume_label.config(foreground='red')
        elif current_vol > 80:
            self.volume_label.config(foreground='orange')
        else:
            self.volume_label.config(foreground='black')

if __name__ == "__main__":
    root = tk.Tk()
    app = VolumeControlApp(root)
    root.mainloop()
