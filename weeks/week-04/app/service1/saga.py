# Создать заказ (NEW) -> Зарезервировать товар -> Списать деньги (PAID) -> Завершить (DONE)

# Состояния заказа
STATES = ('NEW', 'PAID', 'DONE', 'CANCELLED')

# Машина состояний (state, event) -> next_state
TRANSITIONS = {
    ('NEW', 'PAY_OK'): 'PAID',
    ('NEW', 'PAY_FAIL'): 'CANCELLED',
    ('NEW', 'RESERVE_FAIL'): 'CANCELLED',
    ('PAID', 'COMPLETE'): 'DONE',
}
# Терминальные состояния остаются без изменений
TERMINAL = ('DONE', 'CANCELLED')


def next_state(state: str, event: str) -> str:
    """
    Машина состояний Saga.
    Принимает текущее состояние и событие, возвращает следующее состояние.
    """
    if state in TERMINAL:
        return state
    key = (state, event)
    if key in TRANSITIONS:
        return TRANSITIONS[key]
    raise ValueError(f"Неизвестный переход: {state} + {event}")


def compensate_on_payment_failure(cancel_reserve_fn, max_retries=None) -> None:
    """
    Компенсация при ошибке оплаты: отмена резерва товара с retry.
    Если PAY_FAIL — нужно вернуть товар на склад (отменить резерв).
    """
    attempts = 0
    # Пробуем выполнять отмену до успеха или пока не исчерпаем max_retries
    while True:
        try:
            cancel_reserve_fn()  # попытка отменить резерв
            return
        except Exception:
            attempts += 1
            if max_retries is not None and attempts >= max_retries:
                raise