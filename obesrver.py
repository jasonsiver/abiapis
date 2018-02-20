
#!/usr/bin/python3


from tradingapis.bittrex_api import bittrex
from tradingapis.huobi_api import huobi
from tradingapis.bitflyer_api import pybitflyer
from tradingapis.bitbank_api import public_api
from tradingapis.zaif_api.impl import ZaifPublicApi,ZaifTradeApi
from tradingapis.quoine_api import client



from timeit import Timer
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
import time
import threading


#import json

class SendMail:

    def __init__(self,address,username,passwd ):
        self.address = address
        self.username = username
        self.passwd = passwd
        self.s = smtplib.SMTP('smtp.gmail.com', 587)
        self.from_add = 'goozzfgle@gmail.com'
        self.connect_mail_server()

    def connect_mail_server(self):
        try:
            if self.s.ehlo_or_helo_if_needed():
                self.s.ehlo()
            self.s.starttls()
            self.s.ehlo()
            self.s.login(self.username, self.passwd)
            return 0
        except smtplib.SMTPNotSupportedError:
            self.s.login(self.username, self.passwd)
            return 0
        return 1


    def send_email(self, toaddress ,mesage):
        self.connect_mail_server()
        self.s.sendmail(self.from_add, toaddress, mesage)



def print_quoine():
    quoine_api = client.Quoine()
    print(quoine_api.get_product(5))

def print_zaif():
    zaif_api =ZaifPublicApi()
    print(zaif_api.ticker('btc_jpy'))

def print_bittrex():
    bittrex_api = bittrex.Bittrex('', '')
    print(bittrex_api.get_markets())

def print_huobi():
    print(huobi.get_ticker('btcusdt'))

def print_bitflyer():
    bitflyer_api = pybitflyer.API()
    print(bitflyer_api.ticker())

def print_bitbank():
    bitbank_api = public_api.bitbankcc_public()
    print(bitbank_api.get_ticker('eth_btc'))
    print(bitbank_api.get_depth('eth_btc'))



def test_api_time():
    execute_list=['print_bittrex','print_huobi','print_bitflyer','print_bitbank']
    for i in execute_list:
        from_str = 'from __main__ import %s'%(i)
        execute_str = '%s()'%(i)

        t1 = Timer(execute_str, from_str)
        print(t1.timeit(1))

def get_bid_ask_huobi(product_pair):
    if product_pair == '':
        product_pair = 'BTC_USDT'
    elif product_pair =='BTC_ETH':
        product_pair = 'ethbtc'
    elif product_pair =='BTC_LTC':
        product_pair = 'ltcbtc'
    jsons_dict = huobi.get_ticker(product_pair)
    bid = jsons_dict['tick']['bid'][0]
    ask = jsons_dict['tick']['ask'][0]
    return([bid,ask])

def get_bid_ask_bittrex(product_pair):
    if product_pair == '':
        product_pair = 'BTC_USDT'
    elif product_pair =='BTC_ETH':
        product_pair = 'BTC-ETH'
    elif product_pair =='BTC_LTC':
        product_pair = 'BTC-LTC'
    bittrex_api = bittrex.Bittrex('', '')
    #jsons_dict = bittrex_api.get_markets()
    jsons_dict = bittrex_api.get_ticker(product_pair)
    bid = jsons_dict['result']['Bid']
    ask = jsons_dict['result']['Ask']
    return([bid,ask])

def get_bid_ask_bitbank(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 'btc_jpy'
    elif product_pair =='BTC_ETH':
        product_pair = 'eth_btc'
    bitbank_api = public_api.bitbankcc_public()
    jsons_dict = bitbank_api.get_ticker(product_pair)
    ask = float(jsons_dict['sell'])
    bid = float(jsons_dict['buy'])
    return ([bid, ask])

def get_bid_ask_bitflyer(product_pair):
    if product_pair == '':
        product_pair = 'BTC_JPY'
    elif product_pair =='BTC_ETH':
        product_pair = 'ETH_BTC'
    elif product_pair =='BTC_LTC':
        product_pair = 'LTC_BTC'
    bitflyer_api = pybitflyer.API()
    jsons_dict = bitflyer_api.ticker(product_code='%s'%(product_pair))
    bid = jsons_dict['best_bid']
    ask = jsons_dict['best_ask']
    return ([bid, ask])

def get_bid_ask_zaif(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 'btc_jpy'
    else:
        product_pair = ''
    zaif_api =ZaifPublicApi()
    jsons_dict = zaif_api.ticker(product_pair)
    bid = jsons_dict['bid']
    ask = jsons_dict['ask']
    return ([bid, ask])

def get_bid_ask_quoine(product_pair):
    if product_pair == 'BTC_JPY':
        product_pair = 5
    else:
        product_pair = ''

    quoine_api = client.Quoine()
    jsons_dict = quoine_api.get_product(product_pair)
    bid = float(jsons_dict['market_bid'])
    ask = float(jsons_dict['market_ask'])
    #bid = format(bid, '.1f')
    #ask = format(ask, '.1f')
    return([bid, ask])


def calculate_rate(result_bid_ask1,result_bid_ask2, market1 = '', market2 =''):

    if result_bid_ask1[2] != 0 and result_bid_ask2[2] != 0: # if error occurred
        return (-1000000, '', '', 0, 0)

    # if 1's sell bigger than 2's buy
    if result_bid_ask1[0] > result_bid_ask2[1]:
        sell = result_bid_ask1[0]
        buy = result_bid_ask2[1]
        buy_market = market2 # buy at 2 sell at 1
        sell_market = market1
    # if 2's sell bigger than 1's buy
    elif result_bid_ask2[0] > result_bid_ask1[1]:
        sell = result_bid_ask2[0]
        buy = result_bid_ask1[1]
        buy_market = market1 # buy at 1 sell at 2
        sell_market = market2
    else:
        return (-1000000, '', '', 0, 0)

    buy_price = buy
    sell_price = sell

    if market1 != '' and market2 != '' and buy_market != '':
        if buy_market == market1:
            buy = buy * (1+trading_fees(market1)*0.01)
            sell = sell * (1-trading_fees(market2)*0.01)
        elif buy_market == market2:
            buy = buy * (1 + trading_fees(market2) * 0.01)
            sell = sell * (1- trading_fees(market1)*0.01)

    arb_value = sell - buy
    arb_rate = (arb_value/buy)*100


    return (arb_value, buy_market, sell_market, buy_price, sell_price)


def trading_fees(market):

    if market == 'bittrex':
        fees = 0.25
    elif market =='bitflyer':
        fees = 0.13
    elif market == 'bitbank':
        fees = 0.0
    elif market == 'zaif':
        fees = -0.01
    elif market == 'quoine':
        fees = 0.25
    else:
        fees = 0.0

    return(fees)



def write_record(fname,rate,direction,str1,str2):
    fid = open(fname,'a')
    if direction ==1:
        buy = str1
        sell = str2
    else:
        buy = str2
        sell = str1


    time_str = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime())
    write_str = 'buy: %s, sell: %s, profit: %f %% time: %s \n'%(buy,sell,rate,time_str)
    fid.write(write_str)
    fid.close()

def mytimer(time_len):
    global mail_trigger
    while 1:
        time.sleep(time_len)
        mail_trigger = 0

class Mythread(threading.Thread):
    def __init__(self,target,args):
        super(Mythread,self).__init__()
        self.target = target
        self.args = args

    def run(self):
        self.result = self.target(*self.args)
        #print(self.result)
    def get_result(self):
        try:
            return self.result
        except Exception:
            return 1

if __name__ == '__main__':

# initial markets
    trade_threshold = 1000
    product_pair = 'BTC_JPY'
    t_zaif = Mythread(target=get_bid_ask_zaif, args=(product_pair,))
    t_quoine = Mythread(target=get_bid_ask_quoine, args=(product_pair,))
    t_bitbank = Mythread(target=get_bid_ask_bitbank, args=(product_pair,))
    t_bitflyer = Mythread(target=get_bid_ask_bitflyer, args=(product_pair,))

    t_zaif.start()
    t_quoine.start()
    t_bitbank.start()
    t_bitflyer.start()

    zaif_price = [-1, -1, 0] # 1st: bid 2nd: ask 3rd: status
    quoine_price = [-1, -1, 0]
    bitbank_price =[-1, -1, 0]
    bitflyer_price = [-1, -1, 0]

# initial mail server
    address = 'goozzfgle@gmail.com' # change the reciver e-mail address to yours


    username = 'goozzfgle@gmail.com'
    paswd = 'google871225'


    mail_trigger = 0
    mail_timer = Mythread(target=mytimer, args=(20,))
    mail_timer.start()

    arb = [0]*6
    buymarket = ['']*6
    sellmarket = ['']*6
    price_buy_pair = [0]*6
    price_sell_pair = [0]*6

    while 1:
        try:
            t_zaif.run()
            zaif_price[2] = 0
        except Exception:
            print('Zaif Error 1@ %s\n'%formatdate())
            zaif_price[2] = 1

        try:
            t_quoine.run()
            quoine_price[2] = 0
        except Exception:
            print('Quoine Error 1@ %s\n'%formatdate())
            quoine_price[2] = 1

        try:
            t_bitbank.run()
            bitbank_price[2] = 0
        except Exception:
            print('Bitbank Error 1@ %s\n' % formatdate())
            bitbank_price[2] = 1

        try:
            t_bitflyer.run()
            bitflyer_price[2] = 0
        except Exception:
            print('Bitflyer Error 1@ %s\n' % formatdate())
            bitflyer_price[2] = 1

        if zaif_price[2] == 0:
            try:
                t_zaif.join(1)
                [bid,ask] = t_zaif.get_result()
                zaif_price[0] = bid
                zaif_price[1] = ask
            except Exception:
                print('Zaif Error 2@ %s\n' % formatdate())
                zaif_price[2] = 2

        if quoine_price[2] == 0:
            try:
                t_quoine.join(1)
                [bid,ask] = t_quoine.get_result()
                quoine_price[0] = bid
                quoine_price[1] = ask
            except Exception:
                print('Quoine Error 2@ %s\n' % formatdate())
                quoine_price[2] = 2


        if bitbank_price[2] == 0:
            try:
                t_bitbank.join(1)
                [bid,ask] = t_bitbank.get_result()
                bitbank_price[0] = bid
                bitbank_price[1] = ask
            except Exception:
                print('Bitbank Error 2@ %s\n' % formatdate())
                bitbank_price[2] = 2

        if bitflyer_price[2] == 0:
            try:
                t_bitflyer.join(1)
                [bid,ask] = t_bitflyer.get_result()
                bitflyer_price[0] = bid
                bitflyer_price[1] = ask
            except Exception:
                print('Bitflyer Error 2@ %s\n' % formatdate())
                bitflyer_price[2] = 2


        arb[0], buymarket[0], sellmarket[0], price_buy_pair[0] , price_sell_pair[0] = calculate_rate(zaif_price, bitflyer_price, 'zaif', 'bitflyer')
        arb[1], buymarket[1], sellmarket[1], price_buy_pair[1] , price_sell_pair[1] = calculate_rate(zaif_price, bitbank_price, 'zaif', 'bitbank')
        arb[2], buymarket[2], sellmarket[2], price_buy_pair[2] , price_sell_pair[2] = calculate_rate(zaif_price, quoine_price, 'zaif', 'quoine')
        arb[3], buymarket[3], sellmarket[3], price_buy_pair[3] , price_sell_pair[3] = calculate_rate(bitbank_price, bitflyer_price, 'bitbank', 'bitflyer')
        arb[4], buymarket[4], sellmarket[4], price_buy_pair[4] , price_sell_pair[4] = calculate_rate(bitbank_price, quoine_price, 'bitbank', 'quoine')
        arb[5], buymarket[5], sellmarket[5], price_buy_pair[5] , price_sell_pair[5] = calculate_rate(quoine_price, bitflyer_price, 'quoine', 'bitflyer')

        for i in range(0,6):
            if arb[i] > trade_threshold:
                arb_str = 'arb: buy at:%s %f, sell at:%s %f, profit: %f'%(buymarket[i],price_buy_pair[i],sellmarket[i],price_sell_pair[i],arb[i])
                print(arb_str)

                if mail_trigger == 0:
                    mail_str = '%s\n%s'%(arb_str, formatdate(None, True, None))
                    title_str = 'buy:%s sell:%s'%(buymarket[i], sellmarket[i])
                    sender = SendMail(address, username, paswd)
                    msg = MIMEText(mail_str)
                    msg['Subject'] = title_str
                    msg['From'] = username
                    msg['To'] = address
                    msg['Date'] = formatdate()
                    sender.send_email(address, msg.as_string())
                    print('send a mail to %s'%(address))
                    mail_trigger = 1

            #if arb[i] >-100 and arb[i] <100:
            #    print('anit-arb: buy at %s, sell at %s, profit: %f' % (buymarket[i], sellmarket[i], arb[i]))
        time.sleep(1)

    #print_zaif()
    #print_quoine()
    #results_zaif = get_bid_ask_zaif(product_pair)
    #results_bitflyer = get_bid_ask_bitflyer(product_pair)
    #[rate, direction]=calculate_rate(results_zaif, results_bitflyer)

    #try:
    #    try_error(x)
    #except:
    #    print('not_value')
    #product_pair = 'BTC_JPY'

    #print(time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime()))
    #fname1 = '/home/zhang/Templates/recording2.txt'
    #fname2 = '/home/zhang/Templates/recording4.txt'
    #fname3 = '/home/zhang/Templates/recording6.txt'

    #fid = open(fname1,'w')
    #fid.close()
    #fid = open(fname2, 'w')
    #fid.close()
    #fid = open(fname3, 'w')
    #fid.close()
    #threadhold1 = 2
    #threadhold2 = 4
    #threadhold3 = 6
    #str_bitflyer = 'bitflyer'
    #str_bittrex = 'bittrex'
    #str_huobi = 'huobi'
    #str_bitbank = 'bitbank'

    #while 1:
        #results_bitflyer = get_bid_ask_bitflyer(product_pair)
      #  results_bittrex = get_bid_ask_bittrex(product_pair)
      #  results_bitbank = get_bid_ask_bitbank(product_pair)
       # results_huobi = get_bid_ask_huobi(product_pair)
        #compute_and_record(results_bitflyer, results_bittrex, results_bitbank, results_huobi, threadhold1, fname1)
        #compute_and_record(results_bitflyer, results_bittrex, results_bitbank, results_huobi, threadhold2, fname2)
        #compute_and_record(results_bitflyer, results_bittrex, results_bitbank, results_huobi, threadhold3, fname3)
        #time.sleep(10)

