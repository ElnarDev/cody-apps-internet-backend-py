from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
from openai import OpenAI

from app.api.deps import SessionDep, CurrentUser
from app.models.task import TaskCreate, TaskPublic, TaskUpdate, TaskAiRequest
from app.services import task_service

router = APIRouter()

# Definimos lo que el usuario nos enviará
class PromptRequest(BaseModel):
    prompt: str

class PromptSuggestion(BaseModel):
    title: str
    description: str

def get_zhipu_models() -> list[str]:
    """Lee modelos candidatos desde ZHIPU_MODELS (CSV)."""
    raw = os.getenv("ZHIPU_MODELS", "glm-4-plus,glm-4-air,glm-4-flash")
    models = [m.strip() for m in raw.split(",") if m.strip()]
    return models or ["glm-4-plus"]

def get_zhipu_client() -> OpenAI:
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Falta la variable ZHIPU_API_KEY en el entorno del backend."
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )

# Observa que todas las peticiones exigen `current_user: CurrentUser`. 
# Esto hace que nadie anónimo pueda ver ni tocar las tareas. Seguridad de borde por Defecto.

@router.get("/", response_model=list[TaskPublic])
def leer_tareas(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    return task_service.get_tasks(session=session, skip=skip, limit=limit)

@router.post("/", response_model=TaskPublic)
def crear_tarea(session: SessionDep, current_user: CurrentUser, task_in: TaskCreate) -> Any:
    return task_service.create_task(session=session, task_in=task_in)

@router.post("/ai", response_model=TaskPublic)
def crear_tarea_con_ia(session: SessionDep, current_user: CurrentUser, request: TaskAiRequest) -> Any:
    """
    Genera una tarea completa (título + descripción + consejo pirata) usando Gemini a partir de un prompt libre.
    """
    return task_service.create_task_ai(session=session, prompt=request.prompt)

@router.patch("/{task_id}", response_model=TaskPublic)
def actualizar_tarea(session: SessionDep, current_user: CurrentUser, task_id: int, task_in: TaskUpdate) -> Any:
    task_db = task_service.update_task(session=session, task_id=task_id, task_in=task_in)
    if not task_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada ❌")
    return task_db

@router.delete("/{task_id}")
def borrar_tarea(session: SessionDep, current_user: CurrentUser, task_id: int) -> dict:
    deleted = task_service.delete_task(session=session, task_id=task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tarea no encontrada ❌")
    return {"mensaje": f"Tarea {task_id} borrada exitosamente de la base de datos"}

@router.post("/ai-suggest", response_model=PromptSuggestion)
def suggest_task(request: PromptRequest, current_user: CurrentUser) -> PromptSuggestion:
    """
    Recibe un texto en lenguaje natural y la IA extrae el Título y Descripción.
    """
    
    # Instrucciones estrictas para la IA (System Prompt)
    system_prompt = """
    Eres un asistente de productividad. El usuario te dará una frase en lenguaje natural sobre algo que tiene que hacer.
    Tu trabajo es extraer un 'titulo' corto y conciso, y una 'descripcion' más detallada.
    Debes responder EXCLUSIVAMENTE en formato JSON válido, sin Markdown, con esta estructura exacta:
    {"title": "string", "description": "string"}
    """
    
    # Llamada al modelo con fallback de candidatos para evitar fallos por nombre inválido.
    client = get_zhipu_client()
    models = get_zhipu_models()

    response = None
    last_error: str | None = None
    for model_name in models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=0.3, # Baja temperatura para respuestas lógicas y predecibles
            )
            break
        except Exception as exc:
            last_error = str(exc)

    if response is None:
        detail = (
            "No se pudo generar la sugerencia con IA. "
            f"Modelos probados: {', '.join(models)}. "
            f"Último error: {last_error or 'sin detalle'}"
        )
        raise HTTPException(status_code=502, detail=detail)

    content = response.choices[0].message.content
    if not content:
        raise HTTPException(status_code=502, detail="La IA no devolvió contenido.")

    try:
        ai_result = json.loads(content)
        return PromptSuggestion(**ai_result)
    except (json.JSONDecodeError, TypeError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="La IA devolvió un formato inválido. Intenta nuevamente."
        )
