from faster_whisper import WhisperModel

model_size = "kotoba-tech/kotoba-whisper-v1.0-faster"

# Run on GPU with FP16
model = WhisperModel(model_size, device="cpu", compute_type="int8")
# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

vad_threshold = 0.5
chunk_duration = 20.0

import time
start_time = time.time()

segments, info = model.transcribe("esk289.wav",     
                                  word_timestamps=True,
                                  task="transcribe",
                                  language="ja",
      temperature=0,
      beam_size=2,
      best_of=2,
      patience=2,
      vad_filter=True,
      repetition_penalty= 1.5,
      no_repeat_ngram_size= 2,
            vad_parameters=dict(threshold=vad_threshold, max_speech_duration_s=chunk_duration),)

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

print("--- %s seconds ---" % (time.time() - start_time))
