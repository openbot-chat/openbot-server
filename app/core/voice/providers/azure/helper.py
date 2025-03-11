
def generate_right_ssml_text(text: str, voice_id: str, speaking_rate, speaking_pitch, speaking_volume = 1, style = ""):
    attribs = {
        "rate": speaking_rate,
        "pitch": speaking_pitch,
        "volume": speaking_volume,
        "style": style,
    }
    cleaned_attribs_string = ""
    for k, v in attribs.items():
        if not v:
            continue
        cleaned_attribs_string = f"{cleaned_attribs_string} {k}='{v}%'"
    if not cleaned_attribs_string.strip():
        return text, False
    
    smll_text = f"""
      <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
        <voice name='{voice_id}'>
          <mstts:express-as style='{style}'>
            <prosody {cleaned_attribs_string}>{format_text_for_ssml_tags(text)}</prosody>
          </mstts:express-as>
        </voice>
      </speak>
    """
    return smll_text, True

def format_text_for_ssml_tags(text: str):
    tobe_replaced = [("&", "&amp"), ("<", "&lt"), (">", "&gt")]
    for element in tobe_replaced:
        text.replace(element[0], element[1])
    return text