from langchain.prompts import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document as LDocument
from models.api import SummaryChainRequest, ChainResponse
from fastapi import APIRouter, Request
from starlette.types import Send
from api.common.stream_response import StreamingResponse
from chat.handler import AsyncSSEChatResponseCallbackHandler



router = APIRouter()


@router.post("/summarize", response_model=ChainResponse, response_model_exclude_unset=True)
async def summarize(
    request: Request,
    req: SummaryChainRequest,
):
    args = { "chain_type": req.chain_type }
    if req.chain_type == "stuff":
        if req.prompt is not None:
            args["prompt"] = PromptTemplate(template=req.prompt.content, input_variables=req.prompt.input_variables)
    elif req.chain_type == "map_reduce":
        if req.map_prompt is not None:
            args["map_prompt"] = PromptTemplate(template=req.map_prompt.content, input_variables=req.map_prompt.input_variables)

        if req.combine_prompt is not None:
            args["combine_prompt"] = PromptTemplate(template=req.combine_prompt.content, input_variables=req.combine_prompt.input_variables)
    elif req.chain_type == "refine":
        if req.map_prompt is not None:
            args["question_prompt"] = PromptTemplate(template=req.question_prompt.content, input_variables=req.question_prompt.input_variables)

        if req.refine_prompt is not None:
            args["refine_prompt"] = PromptTemplate(template=req.refine_prompt.content, input_variables=req.refine_prompt.input_variables)

    docs = [LDocument(page_content=doc.text) for doc in req.documents]

    if req.streaming:
        async def generate(send: Send):
            llm = await request.app.state.llm_manager.load(req.llm_config, stream_handler=AsyncSSEChatResponseCallbackHandler(send=send))
            chain = load_summarize_chain(llm, verbose=True, **args)
            await chain.arun(docs)
            
        return StreamingResponse(
            generate=generate,
            media_type="text/event-stream",
        )
    else:
        llm = await request.app.state.llm_manager.load(req.llm_config)
        chain = load_summarize_chain(llm, verbose=True, **args)
        output = await chain.arun(docs)
        return ChainResponse(
            text = output,
        )