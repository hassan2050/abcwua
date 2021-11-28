#!/usr/bin/env python3

"""python program to solve the world problems..."""

import os, sys, string, time, logging, math, argparse
from logging import debug,warning,info,error,fatal,critical; warn=warning

_version = "0.1"
import re
import mechanize
from bs4 import BeautifulSoup

import requests

import config

def start1(args):
  if 0:
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders = [('Cookie',cookie), ('User-agent', user_agent)]
    page = br.open(url)
    html_doc = page.read()
    open("output.html", "wb").write(html_doc)

class BillFetch:
  def __init__(self):
    self.cookie_jar = requests.cookies.RequestsCookieJar()
    parts = config.cookie.split("; ")
    for part in parts:
      mparts = part.split('=', 1)
      self.cookie_jar.set(mparts[0], mparts[1])

  def fetchInvoices(self):
    url = "https://www.e-billexpress.com/ebpp/ABCWUA/BillPay"
    #url = "https://www.e-billexpress.com/ebpp/ABCWUA/BillPay/Invoices?tsi=" + tsi

    headers = {'user-agent': config.user_agent}

    if 1:
      r = requests.get(url, headers=headers, cookies=self.cookie_jar)
      html_doc = r.text
      open("invoices.html", "w").write(html_doc)
    else:
      html_doc = open("invoices.html", "r").read()

    soup = BeautifulSoup(html_doc, 'html.parser')

## <div class="item invoice unpaid js-collapse js-no-collapse-mobile" data-amountdue="0.00" data-amountremaining="0.00" data-billingaccount="4277628" data-decryptrefrence="4559639560" data-defaultpayment="0.00" data-expired="False" data-id="843636871" data-minimum-amountdue="0.00" data-paid="False" data-readonly="True" data-selected="False" data-statementdate="7/8/2021" data-total-acct-balance="0.00" id="invoice-row-843636871">

    invoices = []
    
    for div in soup.find_all('div'):
      id = div.attrs.get('id')
      if id and id.startswith("invoice-row-"):
        invoice = {}
        invoices.append(invoice)
        for k,v in div.attrs.items():
          if k.startswith("data-"):
            invoice[k] = v

    return invoices

  def fetchInvoice(self, invoice, fn):
    url = "https://www.e-billexpress.com/ebpp/ABCWUA/Invoice/PDF?billID%%5B0%%5D=%s&tsi=%s" % (invoice['data-id'], config.tsi)
    r = requests.get(url, cookies=self.cookie_jar)
    
    with open(fn, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024): 
        if chunk: # filter out keep-alive new chunks
          f.write(chunk)

  def fetch(self):
    invoices = self.fetchInvoices()

    for invoice in invoices:
      print (invoice)
      logging.debug(invoice['data-id'])
      fn = "%s.pdf" % invoice['data-id']
      if not os.path.exists(fn):
        self.fetchInvoice(invoice, fn)

def start(args):
  bf = BillFetch()
  bf.fetch()

def test():
  logging.warn("Testing")

def parse_args(argv):
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)

  parser.add_argument("-t", "--test", dest="test_flag", default=False, action="store_true", help="Run test function")
  parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Desired console log level")
  parser.add_argument("-d", "--debug", dest="log_level", action="store_const", const="DEBUG", help="Activate debugging")
  parser.add_argument("-q", "--quiet", dest="log_level", action="store_const", const="CRITICAL", help="Quite mode")
  parser.add_argument("files", type=str, nargs='*')

  args = parser.parse_args(argv[1:])

  return parser, args

def main(argv, stdout, environ):
  if sys.version_info < (3, 0): reload(sys); sys.setdefaultencoding('utf8')

  parser, args = parse_args(argv)

  logging.basicConfig(format="[%(asctime)s] %(levelname)-6s %(message)s (%(filename)s:%(lineno)d)", 
                      datefmt="%m/%d %H:%M:%S", level=args.log_level)

  if args.test_flag:  test();   return

  start(args)

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
