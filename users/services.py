import stripe

from config.settings import STRIPE_SECRET_KEY

# Устанавливаем секретный ключ Stripe из настроек
stripe.api_key = STRIPE_SECRET_KEY


def create_stripe_product(name: str, description: str) -> dict:
    """
    Создаёт продукт в Stripe на основе данных из БД.
    Возвращает словарь с данными созданного продукта.
    """
    stripe_product = stripe.Product.create(name=name, description=description)
    return {"id": stripe_product.id, "name": stripe_product.name, "description": stripe_product.description}


def create_stripe_price(stripe_product: dict, amount: int) -> dict:
    """
    Создаёт цену продукта в Stripe.
    amount передаётся в рублях, конвертируется в копейки для Stripe.
    Возвращает словарь с данными созданной цены.
    """
    price = stripe.Price.create(
        currency="rub", unit_amount=amount * 100, product=stripe_product["id"]  # Сумма в копейках
    )
    return {"id": price.id, "unit_amount": price.unit_amount, "currency": price.currency}


def create_stripe_session(price_id: str, success_url: str, cancel_url: str) -> tuple:
    """
    Создаёт сессию оплаты в Stripe.
    Возвращает кортеж: (session_id, session_url).
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.id, session.url
