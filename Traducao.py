import time
import googletrans
import queue

class Traduz:
    def __init__(self, config, text_input_queue: queue.Queue, translated_text_output_queue: queue.Queue):
        self.config = config
        self.translator = googletrans.Translator()
        self.text_input_queue = text_input_queue
        self.translated_text_output_queue = translated_text_output_queue
        self.is_processing = True

    def _perform_translation(self, text: str) -> str:
        try:
            src_lang = self.config.source_language
            dest_lang = self.config.target_language
            
            start_time = time.time()
            translated_text = self.translator.translate(text, src=src_lang, dest=dest_lang).text
            end_time = time.time()
            translation_duration = end_time - start_time
            
            print(f"TRADUÇÃO: '{translated_text}'\nTEMPO TRADUÇÃO: {translation_duration:.2f} segundos.")
            return translated_text
        except Exception as e:
            print(f"Erro ao traduzir texto com googletrans: {e}")
            return ""

    def start_processing(self):
        while self.is_processing:
            try:
                text_to_translate = self.text_input_queue.get(timeout=1)
                if text_to_translate is None:
                    self.is_processing = False
                    print("TranslationProcessor parando...")
                    break

                translated_text = self._perform_translation(text_to_translate)

                if translated_text:
                    self.translated_text_output_queue.put(translated_text)
                    # print(f"Added translated text to TTS queue.")

            except queue.Empty:
                time.sleep(0.1)
                continue
            except Exception as e:
                print(f"Ocorreu um erro inesperado no loop do TranslationProcessor: {e}")
                time.sleep(0.5)

        self.translated_text_output_queue.put(None)
        print("TranslationProcessor thread parou...")

    def stop_processing(self):
        self.is_processing = False