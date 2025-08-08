# main.py
import threading
import queue
import time

from config import Config
from CapturandoAudio import CapturaAudio
from FalaemTexto import AudioemTexto as STTProcessor
from Traducao import Traduz as TranslationProcessor
from TraducaoemAudio import TexttoSpeech

def main():
    audio_capture_queue = queue.Queue() 
    stt_output_text_queue = queue.Queue()
    translation_output_text_queue = queue.Queue()

    config_app = Config()

    tts_processor = TexttoSpeech(config_app, translation_output_text_queue)

    translation_processor = TranslationProcessor(config_app, stt_output_text_queue, translation_output_text_queue)
    translation_thread = threading.Thread(target=translation_processor.start_processing, daemon=True)

    stt_processor = STTProcessor(config_app, audio_capture_queue, stt_output_text_queue)
    stt_thread = threading.Thread(target=stt_processor.start_processing, daemon=True)

    audio_capture = CapturaAudio(config_app, audio_capture_queue)

    try:
        stt_thread.start()
        translation_thread.start()

        print("****Sistema Acionado****Aperte Cntrl+C para SAIR****\n")
        
        audio_capture.iniciar_gravacao()

    except KeyboardInterrupt:
        print("\n****INTERRUPÇÃO POR TECLA APERTADA****sistema parando***\n")
    except Exception as e:
        print(f"****OCORREU ERRO****: {e}\n")
    finally:
        print("****FINALIZANDO SISTEMA****\n")
        audio_capture.parar_gravacao()
        time.sleep(0.5) 
        stt_thread.join(timeout=5)

        if stt_thread.is_alive():
            print("****STT thread ainda não encerrou****")
        
        translation_thread.join(timeout=5)
        if translation_thread.is_alive():
            print("****Tradução thread ainda não encerrou****")
            
        tts_processor.stop_playback()
        tts_processor.processing_thread.join(timeout=5)
        if tts_processor.processing_thread.is_alive():
            print("TTS thread ainda não encerrou****")
            
        print("****SISTEMA ENCERRADO****\n")

if __name__ == "__main__":
    main()