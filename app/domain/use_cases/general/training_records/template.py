import io

import xlsxwriter

from app.infrastructure.orm.general.training_field import TrainingField
from app.infrastructure.database.session import _get_session_factory


def generate_template(format: str = "xlsx") -> tuple[bytes, str, str]:
    db = _get_session_factory()()
    try:
        fields = (
            db.query(TrainingField)
            .filter(TrainingField.status != "DELETED")
            .order_by(TrainingField.order_index)
            .all()
        )
    finally:
        db.close()

    headers = [f.field_key for f in fields]
    labels = {f.field_key: f.label for f in fields}

    if format == "csv":
        return _generate_csv(headers, labels)
    else:
        return _generate_xlsx(headers, labels)


def _generate_csv(headers: list[str], labels: dict[str, str]) -> tuple[bytes, str, str]:
    output = io.StringIO()
    writer = __import__("csv").writer(output)
    writer.writerow([labels.get(h, h) for h in headers])
    content = output.getvalue().encode("utf-8")
    return content, "plantilla_entrenamiento.csv", "text/csv"


def _generate_xlsx(headers: list[str], labels: dict[str, str]) -> tuple[bytes, str, str]:
    buffer = io.BytesIO()
    wb = xlsxwriter.Workbook(buffer, {"in_memory": True})
    ws = wb.add_worksheet("Datos")

    header_format = wb.add_format({
        "bold": True,
        "bg_color": "#D9E1F2",
        "border": 1,
        "text_wrap": True,
        "valign": "vcenter",
    })

    for col, h in enumerate(headers):
        label = labels.get(h, h)
        ws.write(0, col, label, header_format)
        ws.set_column(col, col, max(18, len(label) + 4))

    wb.close()
    buffer.seek(0)
    return buffer.read(), "plantilla_entrenamiento.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
