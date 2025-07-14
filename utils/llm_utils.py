# --------------- utils/llm_utils.py ---------------
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

GROQ_API_KEY = "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"
MODEL_LLM = "llama3-8b-8192"


def generar_justificacion(descripcion):
    prompt = ChatPromptTemplate.from_template(
        "Eres un experto en seguridad. Genera una justificación técnica concisa "
        "(máximo 2 oraciones) en español para esta alerta:\n"
        "Alerta: {alerta}\n\n"
        "Justificación:"
    )

    llm = ChatGroq(temperature=0.7, model_name=MODEL_LLM, api_key=GROQ_API_KEY)
    chain = prompt | llm

    return chain.invoke({"alerta": descripcion}).content