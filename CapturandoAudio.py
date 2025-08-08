import speech_recognition as sr
from config import Config
import time
import queue

class CapturaAudio:
    def __init__(self, config: Config, audio_queue: queue.Queue):
        self.config = config
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=config.sample_rate)
        self.is_recording = False
        self.audio_queue = audio_queue
        

    def iniciar_gravacao(self):
        self.is_recording = True
        self.gravar_e_reconhecer_audio()
    
    def parar_gravacao(self):
        self.is_recording = False
        self.audio_queue.put(None)
        print("*Gravação de áudio parada*")
        
    def gravar_e_reconhecer_audio(self):
        with self.microphone as mic:
            self.recognizer.adjust_for_ambient_noise(mic, duration=1.5)
            print("Pronto! Diga algo.")

            while self.is_recording:
                try:
                    start_time = time.time()
                    audio = self.recognizer.listen(
                        mic,
                        timeout=None,
                        phrase_time_limit=self.config.chunk_duration
                    )
                    end_time = time.time()
                    capta_audio = end_time - start_time
                    
                    
                    self.audio_queue.put(audio)
                    print(f"Capturação de áudio: {capta_audio:.2f} segundos.")

                except sr.WaitTimeoutError:
                    print("Nenhum áudio detectado...")
                    continue

                except sr.UnknownValueError:
                    print("Não entendi, poderia repetir?")
                    continue

                except sr.RequestError as e:
                    print(f"***ERRO durante a requisição: {e}")
                    time.sleep(1)
                    continue

                except Exception as e:
                    print(f"Ocorreu um erro inesperado na captura de áudio: {e}")
                    time.sleep(1)
                    continue

                except KeyboardInterrupt:
                    print("***Captura de áudio interrompida pelo usuário")
                    self.is_recording = False
                    self.audio_queue.put(None)
                    break
