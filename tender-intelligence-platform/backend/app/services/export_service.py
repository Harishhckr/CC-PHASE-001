import csv
from io import StringIO
from typing import List

from app.database.models import Tender


def export_tenders_to_csv(tenders: List[Tender]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tender ID", "Title", "Source", "End Date", "Value"])
    for tender in tenders:
        writer.writerow([tender.tender_id, tender.title, tender.source, tender.end_date, tender.value])
    return output.getvalue()
