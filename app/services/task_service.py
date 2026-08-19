from sqlmodel import Session, select
from app.models.task import Task, TaskCreate, TaskUpdate
from app.core.config import settings
from google import genai
import json
import re

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica.
# Jamás sabe qué es una "Request" o "FastAPI". Separación absoluta.


def get_tasks(session: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    statement = select(Task).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_task_by_id(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)


def create_task(session: Session, task_in: TaskCreate) -> Task:
    task_db = Task.model_validate(task_in)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db


def create_task_ai(session: Session, prompt: str) -> Task:
    title = prompt[:80]
    description = None
    ai_suggestion = None

    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            gen_prompt = (
                f"El usuario quiere crear una tarea sobre: '{prompt}'. "
                "Devuelve ÚNICAMENTE un objeto JSON (sin markdown, sin texto extra) con exactamente estas 3 claves: "
                '"title" (string, máximo 80 caracteres, título de la tarea), '
                '"description" (string, obligatorio, 1 oración que explique qué hay que hacer), '
                '"suggestion" (string, consejo motivador breve como si fueras un pirata). '
                'Ejemplo: {"title":"Hacer queso cheddar","description":"Preparar queso cheddar artesanal siguiendo la receta tradicional.","suggestion":"¡Zarpa hacia los quesos, marinero!"}'
            )
            response = client.models.generate_content(model="gemini-2.0-flash", contents=gen_prompt)
            raw = response.text.strip()
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                title = (data.get("title") or prompt)[:80]
                description = data.get("description") or f"Completar la tarea relacionada con: {prompt}"
                ai_suggestion = data.get("suggestion")
        except Exception as e:
            print(f"Error generando tarea con IA: {e}")
            description = f"Completar la tarea relacionada con: {prompt}"

    task_db = Task(title=title, description=description, ai_suggestion=ai_suggestion)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db


def update_task(session: Session, task_id: int, task_in: TaskUpdate) -> Task | None:
    task_db = get_task_by_id(session, task_id)
    if not task_db:
        return None

    # Ignora valores "Nulos" que vengan del Frontend (Parcheo Parcial)
    update_data = task_in.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(update_data)

    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db


def delete_task(session: Session, task_id: int) -> bool:
    task_db = get_task_by_id(session, task_id)
    if not task_db:
        return False

    session.delete(task_db)
    session.commit()
    return True
