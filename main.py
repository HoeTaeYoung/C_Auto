from vars_funcs import *
# Main Logic

# 로그인
fStart = timeBackup = num_buy = num_sell = minBack = hrBack = 0
# 시작 메세지 슬랙 전송
post_message(myToken, myChannel, "==================================")
post_message(myToken, myChannel, "autotrade start (ver."+VERSION+"))")
post_message(myToken, myChannel, "==================================")

while True:
    try:
        now = datetime.datetime.now()
    # 매일 08시 59분 신규 종목 선정
        if timeBackup != now.hour or fStart == 0 or (now.hour == 8 and now.minute == 59):
            if (fStart == 0) or (now.hour == 8 and now.minute == 59):
                last_trade_time = [now - datetime.timedelta(minutes=10)]*10
            # 신규 종목 선정 및 목표가 계산
                post_message(myToken, myChannel, "=== 종목 선정 시작 : "+str(datetime.datetime.now()))
                if now.hour >= 9:
                    tmp = select_tkrs('day', 2)
                else:
                    tmp = select_tkrs('day', 1)

                tkr_buy[0] = 'KRW-BTC'
                tkr_buy[1] = 'KRW-ETH'
                j = 2
                for i in range(0, 15):
                    if tmp[i] != 'KRW-BTC' and tmp[i] != 'KRW-ETH':
                        tkr_buy[j] = tmp[i]
                        j += 1
                        if j >= 10:
                            break
                num_buy_total = num_sell_total = 0
                post_message(myToken, myChannel, "=== 종목 선정 완료 : "+str(datetime.datetime.now()))
                post_message(myToken, myChannel, str(tkr_buy))
            # 탈락 종목 전량 매도
                post_message(myToken, myChannel, "=== 미포함 종목 매도 : "+str(datetime.datetime.now()))
                balances = upbit.get_balances()
                time.sleep(0.1)
                for b in balances:
                    if b['currency'] != 'KRW' and float(b['avg_buy_price']) > 0:
                        tkr = "KRW-"+b['currency']
                        if tkr not in tkr_buy:
                            if get_balance(tkr,"KRW") > 5000:
                                sell(tkr)
                                num_sell += 1
                            time.sleep(0.1)
                for i in range(0,10):
                    target_price[i] = get_open_price(tkr_buy[i], "day")
            # 잔고 Update
                startBalance = get_totalKRW()
                hourlyBalance = startBalance
                fStart = 1
        # 1시간 마다 매매 결과 송신
            curBalance = get_totalKRW()
            balChange_hr = curBalance - hourlyBalance
            balChngPercent_hr = balChange_hr / hourlyBalance * 100
            balChange_d = curBalance - startBalance
            balChngPercent_d = balChange_d / startBalance * 100
            hourlyBalance = curBalance
            # balance[0] = balance[1] = curBalance * 0.125
            for i in range(0, 10):
                balance[i] = curBalance * 0.095
            num_buy_total += num_buy
            num_sell_total += num_sell
            post_message(myToken, myChannel, "=== Hourly Report ===")
            post_message(myToken, myChannel, " - 잔고 : "+str(round(curBalance))+"원")
            post_message(myToken, myChannel, " - 매수(시간) : "+str(num_buy)+"회, 매도(시간) : "+str(num_sell)+"회")
            post_message(myToken, myChannel, " - 매수(금일) : "+str(num_buy_total)+"회, 매도(금일) : "+str(num_sell_total)+"회")
            post_message(myToken, myChannel, " - 수익(시간) : "+str(round(balChange_hr))+"원 ("+str(round(balChngPercent_hr, 2))+"%)")
            post_message(myToken, myChannel, " - 수익(금일) : "+str(round(balChange_d))+"원 ("+str(round(balChngPercent_d, 2))+"%)")
            num_buy = num_sell = 0
            timeBackup = now.hour


    # 매매 logic
        now = datetime.datetime.now()
        for i in range(0, 10):
            tkr = tkr_buy[i]
            balanceDiff = balance[i] - get_balance(tkr,"KRW")
        # 목표가 Update (9시, 13시, 17시, 21시, 1시, 5시)
        #    if (now.hour % 4 == 1) and (now.minute <= 1):
        #        target_price[i] = get_open_price(tkr, "minute240")
        # 매수
            if balanceDiff > 5000: # and (now > last_trade_time[i] + datetime.timedelta(minutes=5)):
                current = get_current_price(tkr)
                if tick(current) < (current - target_price[i]) < (tick(current) * 10):
                    buy(tkr, balanceDiff)
                    last_trade_time[i] = now
                    num_buy += 1
        # 매도
            elif get_balance(tkr_buy[i],"KRW") > 5000:
                current = get_current_price(tkr)
                if (target_price[i] - current) > tick(current):
                    sell(tkr)
                    last_trade_time[i] = now
                    num_sell += 1
            time.sleep(0.1)

        

    except Exception as e:
        print(e)
        post_message(myToken, myChannel, e)
        time.sleep(1)
