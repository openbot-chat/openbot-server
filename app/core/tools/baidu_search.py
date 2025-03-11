from langchain.utilities.serpapi import SerpAPIWrapper
from langchain.tools.base import BaseTool
from typing import Any, Callable, List, NamedTuple, Optional, Sequence, Tuple
from langchain.agents.tools import Tool
import sys
import json
import requests
import re
    

def extract_strings(d):
    result = ""
    for k, v in d.items():
        if isinstance(v, dict):
            result += extract_strings(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    result += extract_strings(item)
                elif k in ["content", "abstraction"] and isinstance(item, str):
                    result += item
        elif k in ["content", "abstraction"] and isinstance(v, str):
            result += v
    return result



def search(word:str)->str:
    url = 'https://m.baidu.com/s?ip=220.181.38.119&sid=99999&platform=dueros&give=&pu=cuid%40f4Dlgk4jmofDpLqn9pw1j95bDjg-IEqm4uLlfguXviA0A%2Ccua%40_PvjhYa6vhIDJEjPkJAiC_hV2IgbN28lAqqqB%2Ccut%40%2Cosname%40baiduboxapp%2Cctv%402%2Ccen%40cuid_cua_cut%2Ccsrc%40app_box_voice&bd_ck=0&duosqid=dd0b4f26-0c33-11ed-8af8-6c92bf047346_DCS-10-102-111-27-2004-0726000721-1_2%231_0&mmsuse=plat%40dueros&intent=normal&child=1&dumisid=&bot_attr=%7B%22antiporn_threshold%22%3A%220.8%22%2C%22dcs_prefetch_secrawler%22%3A%221%22%2C%22recommendation_switch%22%3A%220%22%2C%22strict_intent_recall%22%3A%221%22%2C%22tts_mode%22%3A%222%22%2C%22use_mms_extend_display%22%3A%221%22%2C%22image_hint_and_search_no_resource%22%3A%221%22%2C%22image_voice_need_display%22%3A%221%22%2C%22voice_filter%22%3A%221%22%2C%22mms_multi_result_template%22%3A%221%22%2C%22iov_no_url_list%22%3A%221%22%2C%22filter_mms_tplname%22%3A%22vid_hor%5C%2F%5C%2F%22%2C%22iov_disable_swan%22%3A%221%22%2C%22iov_native_img_directive%22%3A%221%22%2C%22screen_common_mode%22%3A%221%22%2C%22iov_rewrite_intent%22%3A%221%22%2C%22iov_rank_bk_result%22%3A%221%22%2C%22iov_rewrite_plan%22%3A%22sgminfo4%22%7D&du_stg=1&tn=dushow&more_res_type=&ssid=0&bd_page_type=1&from=0&logid=10668629920597866922&dumisid=4009'
    params = {'word': word}
    response = requests.get(url, params=params)
    try:
        data = json.loads(response.text)
    except Exception as e:
        print("response error:",response.text,url,params)
        raise e
    #print(json.dumps(data['data']['tplData']['asResult'],indent=4,ensure_ascii=False))
    #print(json.dumps(data['data']['tplData']['asResult'],indent=4,ensure_ascii=False))
    # print(json.dumps(data['data']['tplData']['asResult']['item'][0],indent=4,ensure_ascii=False),file=sys.stderr)
    ret=extract_strings(data['data']['tplData']['asResult'])
    ret = re.sub("[\u0001\u0002\u0003\u0004\u0005]", "", ret)
    # print(ret[:800],file=sys.stderr)
    return ret[:800]

def get_baidu_search_api(**kwargs: Any) -> BaseTool:
    return Tool(
        name="BaiduSearch",
        description="Baidu search engine. Useful for when you need to answer questions about current events or chinese content. Input should be a chinese search query.",
        func=search,
        coroutine=None,
    )

if __name__=="__main__":
    print(search("火车为什么能跑"))