from contextvars import ContextVar

empresa_id_var: ContextVar[int | None] = ContextVar("empresa_id", default=None)


def get_empresa_id() -> int | None:
    return empresa_id_var.get()


def set_empresa_id(empresa_id: int | None):
    empresa_id_var.set(empresa_id)


def clear_empresa_id():
    empresa_id_var.set(None)