import os
import datetime
import locale
from termcolor import colored
from terminaltables import AsciiTable

locale.setlocale(locale.LC_ALL, '')


class Print:
    def info(self, ticks, wallets):
        os.system('clear')

        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        table_info = [
            [
                time,
                'GDAX Price',
                'CEX Price',
                'GDAX Balance',
                'CEX Balance',
                'TOTAL'
            ],
            [
                'USD',
                '---',
                '---',
                locale.currency(wallets['gdax']['usd']['balance'], grouping=True),
                locale.currency(wallets['cex']['usd']['balance'], grouping=True),
                ''
            ],

            [
                'ETH',
                colored(locale.currency(ticks['gdax']['eth']['bid'], grouping=True), 'green') + ' | ' + colored(
                    locale.currency(ticks['gdax']['eth']['ask'], grouping=True), 'red'),
                colored(locale.currency(ticks['cex']['eth']['bid'], grouping=True), 'green') + ' | ' + colored(
                    locale.currency(ticks['cex']['eth']['ask'], grouping=True), 'red'),
                round(wallets['gdax']['eth']['balance'], 3),
                round(wallets['cex']['eth']['balance'], 3),
                ''
            ],
            [
                'BTC',
                colored(locale.currency(ticks['gdax']['btc']['bid'], grouping=True), 'green') + ' | ' + colored(
                    locale.currency(ticks['gdax']['btc']['ask'], grouping=True), 'red'),
                colored(locale.currency(ticks['cex']['btc']['bid'], grouping=True), 'green') + ' | ' + colored(
                    locale.currency(ticks['cex']['btc']['ask'], grouping=True), 'red'),
                round(wallets['gdax']['btc']['balance'], 3),
                round(wallets['cex']['btc']['balance'], 3),
                ''
            ],
            [
                'SUMMARY',
                '',
                '',
                '',
                '',
                ''

            ]
        ]

        table_i = AsciiTable(table_info)
        table_i.inner_row_border = True
        print table_i.table
        print "\n"

    def delta(self, deltas):
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        eth_gdax_to_cex = colored(str(round(deltas['gdaxToCex']['eth']['per'], 2)) + "%", 'red')
        btc_gdax_to_cex = colored(str(round(deltas['gdaxToCex']['btc']['per'], 2)) + "%", 'red')
        eth_cex_to_gdax = colored(str(round(deltas['cexToGdax']['eth']['per'], 2)) + "%", 'red')
        btc_cex_to_gdax = colored(str(round(deltas['cexToGdax']['btc']['per'], 2)) + "%", 'red')

        if deltas['gdaxToCex']['eth']['per'] > 0:
            eth_gdax_to_cex = colored(str(round(deltas['gdaxToCex']['eth']['per'], 2)) + "%", 'green')

        if deltas['gdaxToCex']['btc']['per'] > 0:
            btc_gdax_to_cex = colored(str(round(deltas['gdaxToCex']['btc']['per'], 2)) + "%", 'green')

        if deltas['cexToGdax']['eth']['per'] > 0:
            eth_cex_to_gdax = colored(str(round(deltas['cexToGdax']['eth']['per'], 2)) + "%", 'green')

        if deltas['cexToGdax']['btc']['per'] > 0:
            btc_cex_to_gdax = colored(str(round(deltas['cexToGdax']['btc']['per'], 2)) + "%", 'green')

        table_delta = [
            [
                time,
                'GDAX -> CEX',
                'CEX -> GDAX'
            ],
            [
                'ETH',
                eth_gdax_to_cex,
                eth_cex_to_gdax,

            ],
            [
                'BTC',
                btc_gdax_to_cex,
                btc_cex_to_gdax
            ]
        ]

        table_d = AsciiTable(table_delta)
        table_d.inner_row_border = True
        print table_d.table

        print "\n\n"
