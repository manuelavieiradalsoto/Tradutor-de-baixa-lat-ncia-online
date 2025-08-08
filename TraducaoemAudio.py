from gtts import gTTS
import os
import threading
import queue
import time
import tempfile
import pygame


if not pygame.mixer.get_init():
    pygame.mixer.init()

class AudioProcessor:
    def __init__(self, audio_queue: queue.Queue, output_base_dir="outputs"):
        self.audio_queue = audio_queue
        self.output_base_dir = output_base_dir
        self.processing_thread = threading.Thread(target=self._process_audio_queue, daemon=True)
        self.processing_thread.start()

    def _process_audio_queue(self):
        while True:
            audio_path = None
            try:
                audio_path = self.audio_queue.get(timeout=1)
                if audio_path is None:
                    break

                # print(f"Playing audio: {audio_path}")
                try:
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except pygame.error as e:
                    print(f"Error playing audio file {audio_path}: {e}")
                finally:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()

                    if audio_path and os.path.exists(audio_path):
                        try:
                            os.remove(audio_path)
                            # print(f"limpando arquivo: {audio_path}")
                        except OSError as e:
                            print(f"***ERRO ao deletar {audio_path}, ERRO: {e}")

            except queue.Empty:
                time.sleep(0.5)
            except Exception as e:
                print(f"***ERRO ao processar thread TTS: {e}")

    def add_to_queue(self, audio_path: str):
        self.audio_queue.put(audio_path)
        # print(f"Added {audio_path} to audio queue.")

    def stop(self):
        self.audio_queue.put(None)
        self.processing_thread.join()
        print("AudioProcessor parando...")


class TexttoSpeech:
    def __init__(self, config, tts_input_queue: queue.Queue):
        self.config = config
        self.output_base_dir = "outputs"
        if not os.path.exists(self.output_base_dir):
            os.makedirs(self.output_base_dir)
            print(f"CRIADO output directory: {self.output_base_dir}")
        self.audio_queue = queue.Queue()
        self.audio_processor = AudioProcessor(self.audio_queue, self.output_base_dir)
        self.tts_input_queue = tts_input_queue
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._process_tts_queue, daemon=True)
        self.processing_thread.start()

    def _process_tts_queue(self):
        while self.is_processing:
            try:
                text = self.tts_input_queue.get(timeout=1)
                if text is None:
                    self.is_processing = False
                    print("TexttoSpeech parando...")
                    break

                if not text.strip():
                    print("***TEXTO VAZIO EM TTS...")
                    continue

                tts = gTTS(text=text, lang=self.config.target_language, slow=False)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=self.output_base_dir) as fp:
                    audio_filepath = fp.name
                    tts.save(audio_filepath)
                # print(f"salvo em '{audio_filepath}'")

                self.audio_processor.add_to_queue(audio_filepath)

            except queue.Empty:
                time.sleep(0.1)
                continue
            except Exception as e:
                print(f"***ERRO em TTS, ERRO: {e}")
                time.sleep(0.5)
        
        self.audio_processor.stop()
        print("TexttoSpeech processing thread stopped.")


    def stop_playback(self):
        self.is_processing = False
        self.tts_input_queue.put(None)
        self.processing_thread.join()