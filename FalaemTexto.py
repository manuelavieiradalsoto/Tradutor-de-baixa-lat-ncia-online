import speech_recognition as sr
import time
import queue


class AudioemTexto:
    def __init__(self, config, audio_input_queue: queue.Queue, text_output_queue: queue.Queue):
        self.config = config
        self.recognizer = sr.Recognizer()
        self.audio_input_queue = audio_input_queue
        self.text_output_queue = text_output_queue
        self.is_processing = True

    def _google_stt(self, audio):
        try:
            start_time = time.time()
            text = self.recognizer.recognize_google(
                audio,
                language=self.config.source_language
            )
            end_time = time.time()
            duration = end_time - start_time
            return text, duration
        except sr.UnknownValueError:
            print("Google STT não conseguiu entender o áudio.")
            return None, 0.0
        except sr.RequestError as e:
            print(f"Erro na requisição do Google STT; {e}")
            return None, 0.0
        except Exception as e:
            print(f"Ocorreu um erro inesperado no Google STT: {e}")
            return None, 0.0

    def start_processing(self):
        while self.is_processing:
            try:
                audio = self.audio_input_queue.get(timeout=1)
                if audio is None:
                    self.is_processing = False
                    print("STTProcessor parando...")
                    break

                text_recognized, processing_time = self._google_stt(audio)

                if text_recognized:
                    self.text_output_queue.put(text_recognized)
                    print(f"STT: '{text_recognized}'\nTEMPO STT: {processing_time:.2f} segundos.")

            except queue.Empty:
                time.sleep(0.1)
                continue

            except Exception as e:
                print(f"Ocorreu um erro inesperado no loop do STTProcessor: {e}")
                time.sleep(0.5)

        self.text_output_queue.put(None)
        print("STTProcessor thread parou...")

    def stop_processing(self):
        self.is_processing = False