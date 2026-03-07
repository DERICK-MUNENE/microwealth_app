import pdfplumber
import re

def parse_transaction_pdf(pdf_path: str):
    transactions = []
    total_paid_in = 0.0
    total_paid_out = 0.0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")

            for line in lines:
                values = re.findall(r"([\d,]+\.\d{2})", line)
                if len(values) == 2:
                    paid_in = float(values[0].replace(",", ""))
                    paid_out = float(values[1].replace(",", ""))

                    description = line.split(values[0])[0].strip() or "Transaction"

                    if paid_in > 0:
                        total_paid_in += paid_in
                        transactions.append({
                            "description": description,
                            "amount": paid_in
                        })

                    if paid_out > 0:
                        total_paid_out += paid_out
                        transactions.append({
                            "description": description,
                            "amount": -paid_out
                        })

    return {
        "income": round(total_paid_in, 2),
        "expenses": round(total_paid_out, 2),
        "net_cashflow": round(total_paid_in - total_paid_out, 2),
        "transactions": transactions
    }
