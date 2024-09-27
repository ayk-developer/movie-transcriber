import os
from tqdm import tqdm
import srt
import pysrt
import copy, datetime

from faster_whisper import WhisperModel, BatchedInferencePipeline

from whisper_assist_functions import *

model_size = "whisper-large-v2-japanese-5k-steps-ct2"
model = WhisperModel(model_size, device="cpu", compute_type="int8")
batched_model = BatchedInferencePipeline(model=model,language="ja",chunk_length=15)

def run_whisper_wrapper(
    audio_path,
    language = "japanese",
    task = "transcribe",
    vad_threshold = 0.4,
    chunk_duration = 30.0,
    new_vocabulary = "",
    condition_on_previous_text = False
    ):


    # some sanity checks
    assert vad_threshold >= 0.01
    assert chunk_duration >= 0.1
    assert audio_path != ""
    assert language != ""
    language = language.lower()


    if new_vocabulary.strip() == "":
      new_vocabulary = None

    audiofilebasename = os.path.basename(os.path.splitext(audio_path)[0])
    subfolder = ".subs.original"

    # Get the directory of the audio file
    audiofile_dir = os.path.dirname(audio_path)

    # Construct the subfolder path
    subfolder_path = os.path.join(audiofile_dir, subfolder)

    # Create the subfolder if it doesn't exist
    os.makedirs(subfolder_path, exist_ok=True)

    print("Folder Created")

    if (task=="translate"):
      out_path = os.path.join(subfolder_path, audiofilebasename + ".en" + ".srt")
      out_path_pre = os.path.join(subfolder_path, audiofilebasename + ".en" + ".original.srt")
    else:
      out_path = os.path.join(subfolder_path, audiofilebasename + ".ja" + ".srt")
      out_path_pre = os.path.join(subfolder_path, audiofilebasename + ".ja" + ".original.srt")

    print("Running Whisper … PLEASE WAIT")
    segments, info = batched_model.transcribe(
        audio_path,
        batch_size =16,      
        word_timestamps=True,
        language="ja",
        temperature=0,
      beam_size=3,
      best_of=2,
      patience=2,
      repetition_penalty= 1.5,
      no_repeat_ngram_size= 2,
    )


    PROTOFLAG = False
    absfolderpath = os.path.dirname(os.path.abspath(audio_path))

    subs = []
    segment_info = []
    timestamps = 0.0  # for progress bar

    #with tqdm(total=info.duration, bar_format=TQDM_FORMAT) as pbar:
    with tqdm(total=info.duration) as pbar:
      for i, seg in enumerate(segments, start=1):
        # Keep segment info for debugging
        segment_info.append(seg)

        if PROTOFLAG == True :

            # make a deep copy of each entry
            temp_seg = copy.deepcopy(seg)

            # Clean up possible hallucination
            if (task == "transcribe"):
                temp_seg = sanitiseHallucinationJA(temp_seg, absfolderpath)
            elif (task == "translate"):
                temp_seg = sanitiseHallucinationEN(temp_seg, absfolderpath)
            else:
                print("\n ==== sanitisation funtion NOT performed! ==== \n")


        # Add to SRT list
        subs.append(srt.Subtitle(
          index=i,
          start=datetime.timedelta(seconds=seg.start),
          end=datetime.timedelta(seconds=seg.end),
          content=seg.text.strip(),
        ))
        pbar.update(seg.end - timestamps)
        timestamps = seg.end
      if timestamps < info.duration:
        pbar.update(info.duration - timestamps)
    
    clean_subs = []
    last_line_garbage = False
    for i in range(len(subs)):
        c = clean_text(subs[i].content)
        is_garbage = True
        for w in c.split(" "):
            w_tmp = w.strip()
            if w_tmp == "":
                continue
            if w_tmp in GARBAGE_LIST2:
                continue
            elif w_tmp in NEED_CONTEXT_LINES and last_line_garbage:
                continue
            else:
                is_garbage = False
                break
        if not is_garbage:
            clean_subs.append(subs[i])
        last_line_garbage = is_garbage
    with open(out_path, mode="w", encoding="utf8") as f:
        f.write(srt.compose(clean_subs))
    print("\nDone! Subs being written to", out_path)



    prohibited_phrases_arg = [GARBAGE_LIST2, suppress_high, garbage_list]

    deepl_flag = False


    final_srt = clean_srt_file_japanese(out_path, ".", prohibited_phrases_arg)

    return final_srt



    #print("Downloading SRT file:")
    #g_files.download(out_path)
    

    #for debugging only
    #with open("segment_info.debug.json", mode="w", encoding="utf8") as f:
    #  json.dump(segment_info, f, indent=4)
'''
    # DeepL translation
    translate_error = False
    if deepl_flag:
      print("Translating with DeepL …")
      with open(out_path_pre, "w", encoding="utf8") as f:
        f.write(srt.compose(subs))
      print("(Japanese original subs saved to", out_path_pre, ")")

      lines = []
      for i in range(len(subs)):
        if language == "japanese":
          if subs[i].content[-1] not in PUNCT_MATCH:
            subs[i].content += "。"
          subs[i].content = "「" + subs[i].content + "」"
        else:
          if subs[i].content[-1] not in PUNCT_MATCH:
            subs[i].content += "."
          subs[i].content = '"' + subs[i].content + '"'
      for i in range(len(subs)):
        lines.append(subs[i].content)

      grouped_lines = []
      english_lines = []
      for i, l in enumerate(lines):
        if i % 30 == 0:
          # Split lines into smaller groups, to prevent error 413
          grouped_lines.append([])
          if i != 0:
            # Include previous 3 lines, to preserve context between splits
            grouped_lines[-1].extend(grouped_lines[-2][-3:])
        grouped_lines[-1].append(l.strip())

      try:
        translator = deepl.Translator(deepl_authkey)
        for i, n in enumerate(tqdm(grouped_lines)):
          x = ["\n".join(n).strip()]
          if language == "japanese":
            result = translator.translate_text(x, source_lang="JA", target_lang=deepl_target_lang)
          else:
            result = translator.translate_text(x, target_lang=deepl_target_lang)
          english_tl = result[0].text.strip().splitlines()
          assert len(english_tl) == len(n), f"Invalid translation line count ({len(english_tl)} vs {len(n)})"
          if i != 0:
            english_tl = english_tl[3:]
          for e in english_tl:
            english_lines.append(
              e.strip().translate(REMOVE_QUOTES).replace("’", "'")
            )
        for i, e in enumerate(english_lines):
          subs[i].content = e
      except Exception as e:
        print("DeepL translation error:", e)
        print("(downloading untranslated version instead)")
        translate_error = True

'''

    # Write SRT file

      # Removal of garbage lines

if __name__ == "__main__":
   print("HERE")
   videos = []
   for i in videos:
        run_whisper_wrapper(audio_path=i)