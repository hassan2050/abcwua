#!/usr/bin/env python3

import os
import logging
import argparse
import requests
from bs4 import BeautifulSoup
import config

BASE_URL = "https://www.e-billexpress.com/ebpp/ABCWUA"
#url = "https://www.e-billexpress.com/ebpp/ABCWUA/BillPay/Invoices?tsi=" + tsi

class BillFetch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.user_agent})
        
        # Parse cookie string into session
        for part in config.cookie.split("; "):
            if '=' in part:
                k, v = part.split('=', 1)
                self.session.cookies.set(k, v)

    def fetch_invoices(self) -> list[dict]:
        url = f"{BASE_URL}/BillPay"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch invoices page: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        invoices = []
        
        for div in soup.find_all('div', id=lambda x: x and x.startswith('invoice-row-')):
            invoice_data = {
                key[5:]: val for key, val in div.attrs.items() if key.startswith('data-')
            }
            invoices.append(invoice_data)

        return invoices

    def download_pdf(self, invoice_id: str, filename: str):
        url = f"{BASE_URL}/Invoice/PDF"
        params = {
            'billID[0]': invoice_id,
            'tsi': config.tsi
        }
        
        try:
            with self.session.get(url, params=params, stream=True, timeout=15) as r:
                r.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            logging.info(f"Downloaded {filename}")
        except requests.RequestException as e:
            logging.error(f"Failed to download PDF for invoice {invoice_id}: {e}")

    def run(self):
        invoices = self.fetch_invoices()
        for invoice in invoices:
            invoice_id = invoice.get('id')
            if not invoice_id:
                continue

            output_file = f"{invoice_id}.pdf"
            if not os.path.exists(output_file):
                self.download_pdf(invoice_id, output_file)

def main():
    parser = argparse.ArgumentParser(description="Fetch ABCWUA water utility bills.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    fetcher = BillFetch()
    fetcher.run()

if __name__ == "__main__":
    main()
