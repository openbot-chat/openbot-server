import os
from typing import List
import azure.cognitiveservices.speech as speechsdk
from models.voice import VoiceSchema, SayRequest, SayResponse
from models.locale import LocaleSchemaBase
from ..voice_provider import VoiceProvider
import base64
from .helper import generate_right_ssml_text
from asyncer import asyncify



class AzureVoiceProvider(VoiceProvider):
    def __init__(self):
        self.subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
        self.service_region = os.getenv("AZURE_REGION")
        # self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
        speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.service_region)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    async def fetch_voice_list(self, language: str = "en-US") -> List[VoiceSchema]:
        def fetch() -> List[VoiceSchema]:
            result: speechsdk.SynthesisVoicesResult = self.speech_synthesizer.get_voices_async(language).get()
            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                voices: List[VoiceSchema] = []
                for voice_info in result.voices:
                    voices.append(
                        VoiceSchema(
                            provider="azure",
                            name=voice_info.local_name,
                            gender="male" if voice_info.gender == speechsdk.SynthesisVoiceGender.Female else "female",
                            identifier=voice_info.short_name,
                            language=voice_info.locale,
                            styles=voice_info.style_list,
                        )
                    )
                return voices
            elif result.reason == speechsdk.ResultReason.Canceled:
                raise Exception("Speech synthesis canceled; error details: {}".format(result.error_details))    
        return await asyncify(fetch)()


    async def say(self, req: SayRequest) -> SayResponse:
        speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.service_region)
        speech_config.speech_synthesis_voice_name = req.identifier
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        text, use_ssml = generate_right_ssml_text(req.text, req.identifier, req.rate, req.pitch, req.volume, req.style)

        def generate_audio() -> str:
          return speech_synthesizer.speak_text_async(text).get() if not use_ssml else speech_synthesizer.speak_ssml_async(text).get()

        speech_synthesis_result: speechsdk.SpeechSynthesisResult = await asyncify(generate_audio)()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return SayResponse(
                format="base64",
                duration=speech_synthesis_result.audio_duration.seconds,
                data=base64.b64encode(speech_synthesis_result.audio_data),
            )

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    raise Exception("Error details: {}".format(cancellation_details.error_details))

    async def list_locales(self) -> List[LocaleSchemaBase]:
        return [
            LocaleSchemaBase(locale="af-ZA", label="Afrikaans (South Africa)"),
            LocaleSchemaBase(locale="am-ET", label="Amharic (Ethiopia)"),
            LocaleSchemaBase(locale="ar-AE", label="Arabic (United Arab Emirates)"),
            LocaleSchemaBase(locale="ar-BH", label="Arabic (Bahrain)",),
            LocaleSchemaBase(locale="ar-DZ", label="Arabic (Algeria)"),
            LocaleSchemaBase(locale="ar-EG", label="Arabic (Egypt)"),
            LocaleSchemaBase(locale="ar-IQ", label="Arabic (Iraq)"),
            LocaleSchemaBase(locale="ar-JO", label="Arabic (Jordan)"),
            LocaleSchemaBase(locale="ar-KW", label="Arabic (Kuwait)"),
            LocaleSchemaBase(locale="ar-LB", label="Arabic (Lebanon)"),
            LocaleSchemaBase(locale="ar-LY", label="Arabic (Libya)"),
            LocaleSchemaBase(locale="ar-MA", label="Arabic (Morocco)"),
            LocaleSchemaBase(locale="ar-OM", label="Arabic (Oman)"),
            LocaleSchemaBase(locale="ar-QA", label="Arabic (Qatar)"),
            LocaleSchemaBase(locale="ar-SA", label="Arabic (Saudi Arabia)"),
            LocaleSchemaBase(locale="ar-SY", label="Arabic (Syria)"),
            LocaleSchemaBase(locale="ar-TN", label="Arabic (Tunisia)"),
            LocaleSchemaBase(locale="ar-YE", label="Arabic (Yemen)"),
            LocaleSchemaBase(locale="az-AZ", label="Azerbaijani (Latin, Azerbaijan)"),
            LocaleSchemaBase(locale="bg-BG", label="Bulgarian (Bulgaria)"),
            LocaleSchemaBase(locale="bn-BD", label="Bangla (Bangladesh)"),
            LocaleSchemaBase(locale="bn-IN", label="Bengali (India)"),
            LocaleSchemaBase(locale="bs-BA", label="Bosnian (Bosnia and Herzegovina)"),
            LocaleSchemaBase(locale="ca-ES", label="Catalan (Spain)"),
            LocaleSchemaBase(locale="cs-CZ", label="Czech (Czechia)"),
            LocaleSchemaBase(locale="cy-GB", label="Welsh (United Kingdom)"),
            LocaleSchemaBase(locale="da-DK", label="Danish (Denmark)"),
            LocaleSchemaBase(locale="de-AT", label="German (Austria)"),
            LocaleSchemaBase(locale="de-CH", label="German (Switzerland)"),
            LocaleSchemaBase(locale="de-DE", label="German (Germany)"),
            LocaleSchemaBase(locale="el-GR", label="Greek (Greece)"),
            LocaleSchemaBase(locale="en-AU", label="English (Australia)"),
            LocaleSchemaBase(locale="en-CA", label="English (Canada)"),
            LocaleSchemaBase(locale="en-GB", label="English (United Kingdom)"),
            LocaleSchemaBase(locale="en-HK", label="English (Hong Kong SAR)"),
            LocaleSchemaBase(locale="en-IE", label="English (Ireland)"),
            LocaleSchemaBase(locale="en-IN", label="English (India)"),
            LocaleSchemaBase(locale="en-KE", label="English (Kenya)"),
            LocaleSchemaBase(locale="en-NG", label="English (Nigeria)"),
            LocaleSchemaBase(locale="en-NZ", label="English (New Zealand)"),
            LocaleSchemaBase(locale="en-PH", label="English (Philippines)"),
            LocaleSchemaBase(locale="en-SG", label="English (Singapore)"),
            LocaleSchemaBase(locale="en-TZ", label="English (Tanzania)"),
            LocaleSchemaBase(locale="en-US", label="English (United States)"),
            LocaleSchemaBase(locale="en-ZA", label="English (South Africa)"),
            LocaleSchemaBase(locale="es-AR", label="Spanish (Argentina)"),
            LocaleSchemaBase(locale="es-BO", label="Spanish (Bolivia)"),
            LocaleSchemaBase(locale="es-CL", label="Spanish (Chile)"),
            LocaleSchemaBase(locale="es-CO", label="Spanish (Colombia)"),
            LocaleSchemaBase(locale="es-CR", label="Spanish (Costa Rica)"),
            LocaleSchemaBase(locale="es-CU", label="Spanish (Cuba)"),
            LocaleSchemaBase(locale="es-DO", label="Spanish (Dominican Republic)"),
            LocaleSchemaBase(locale="es-EC", label="Spanish (Ecuador)"),
            LocaleSchemaBase(locale="es-ES", label="Spanish (Spain)"),
            LocaleSchemaBase(locale="es-GQ", label="Spanish (Equatorial Guinea)"),
            LocaleSchemaBase(locale="es-GT", label="Spanish (Guatemala)"),
            LocaleSchemaBase(locale="es-HN", label="Spanish (Honduras)"),
            LocaleSchemaBase(locale="es-MX", label="Spanish (Mexico)"),
            LocaleSchemaBase(locale="es-NI", label="Spanish (Nicaragua)"),
            LocaleSchemaBase(locale="es-PA", label="Spanish (Panama)"),
            LocaleSchemaBase(locale="es-PE", label="Spanish (Peru)"),
            LocaleSchemaBase(locale="es-PR", label="Spanish (Puerto Rico)"),
            LocaleSchemaBase(locale="es-PY", label="Spanish (Paraguay)"),
            LocaleSchemaBase(locale="es-SV", label="Spanish (El Salvador)"),
            LocaleSchemaBase(locale="es-US", label="Spanish (United States)"),
            LocaleSchemaBase(locale="es-UY", label="Spanish (Uruguay)"),
            LocaleSchemaBase(locale="es-VE", label="Spanish (Venezuela)"),
            LocaleSchemaBase(locale="et-EE", label="Estonian (Estonia)"),
            LocaleSchemaBase(locale="eu-ES", label="Basque"),
            LocaleSchemaBase(locale="fa-IR", label="Persian (Iran)"),
            LocaleSchemaBase(locale="fi-FI", label="Finnish (Finland)"),
            LocaleSchemaBase(locale="fil-PH", label="Filipino (Philippines)"),
            LocaleSchemaBase(locale="fr-BE", label="French (Belgium)"),
            LocaleSchemaBase(locale="fr-CA", label="French (Canada)"),
            LocaleSchemaBase(locale="fr-CH", label="French (Switzerland)"),
            LocaleSchemaBase(locale="fr-FR", label="French (France)"),
            LocaleSchemaBase(locale="ga-IE", label="Irish (Ireland)"),
            LocaleSchemaBase(locale="gl-ES", label="Galician"),
            LocaleSchemaBase(locale="gu-IN", label="Gujarati (India)"),
            LocaleSchemaBase(locale="he-IL", label="Hebrew (Israel)"),
            LocaleSchemaBase(locale="hi-IN", label="Hindi (India)"),
            LocaleSchemaBase(locale="hr-HR", label="Croatian (Croatia)"),
            LocaleSchemaBase(locale="hu-HU", label="Hungarian (Hungary)"),
            LocaleSchemaBase(locale="hy-AM", label="Armenian (Armenia)"),
            LocaleSchemaBase(locale="id-ID", label="Indonesian (Indonesia)"),
            LocaleSchemaBase(locale="is-IS", label="Icelandic (Iceland)"),
            LocaleSchemaBase(locale="it-IT", label="Italian (Italy)"),
            LocaleSchemaBase(locale="ja-JP", label="Japanese (Japan)"),
            LocaleSchemaBase(locale="jv-ID", label="Javanese (Latin, Indonesia)"),
            LocaleSchemaBase(locale="ka-GE", label="Georgian (Georgia)"),
            LocaleSchemaBase(locale="kk-KZ", label="Kazakh (Kazakhstan)"),
            LocaleSchemaBase(locale="km-KH", label="Khmer (Cambodia)"),
            LocaleSchemaBase(locale="kn-IN", label="Kannada (India)"),
            LocaleSchemaBase(locale="ko-KR", label="Korean (Korea)"),
            LocaleSchemaBase(locale="lo-LA", label="Lao (Laos)"),
            LocaleSchemaBase(locale="lt-LT", label="Lithuanian (Lithuania)"),
            LocaleSchemaBase(locale="lv-LV", label="Latvian (Latvia)"),
            LocaleSchemaBase(locale="mk-MK", label="Macedonian (North Macedonia)"),
        ]