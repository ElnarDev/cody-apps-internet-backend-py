from google import genai
from sqlmodel import Session, select

from app.core.config import settings
from app.models.review import Review, ReviewCreate

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica de negocio.
# Es agnóstica de FastAPI y de la capa de transporte/web.


def get_reviews_by_product(
    session: Session, product_id: int, skip: int = 0, limit: int = 100
) -> list[Review]:
    statement = (
        select(Review).where(Review.product_id == product_id).offset(skip).limit(limit)
    )
    return list(session.exec(statement).all())


def create_review(
    session: Session, review_in: ReviewCreate, user_id: int, product_id: int
) -> Review:
    review_db = Review(
        rating=review_in.rating,
        comment=review_in.comment,
        user_id=user_id,
        product_id=product_id,
    )

    # --- 🤖 ANÁLISIS DE SENTIMIENTO CON IA ---
    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = (
                f"Eres un experto en productos de hogar y frutas con años de experiencia en análisis de calidad. "
                f"Un cliente ha dejado la siguiente reseña con una calificación de {review_db.rating}/5 estrellas: "
                f"'{review_db.comment}'. "
                f"En un máximo de 2 oraciones, redacta un análisis de sentimiento profesional sobre esta reseña "
                f"y refuerza o contextualiza la opinión del cliente desde tu experiencia experta."
            )

            # Cambiado a 'gemini-2.5-flash' (o 'gemini-1.5-flash')
            response = client.models.generate_content(
                model="gemini-flash-latest", contents=prompt
            )

            if response.text:
                review_db.ai_analysis = response.text.strip()
            else:
                print("⚠️ Gemini devolvió una respuesta vacía.")

        except Exception as e:  # noqa: BLE001
            print(f"❌ Error generando análisis de reseña con IA: {e}")
    else:
        print("⚠️ GEMINI_API_KEY no está configurada en settings.")
    # ------------------------------------------------------------

    session.add(review_db)
    session.commit()
    session.refresh(review_db)
    return review_db
