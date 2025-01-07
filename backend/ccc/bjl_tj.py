# coding: utf-8

import re
import time


def main():
    xue = input("输入靴号：")
    n = int(input("输入局号："))
    # 初始资金 w
    w = 500
    with open(f"bjl_{d}_{xue}.txt", "a+") as fn:
        if n == 1:
            fn.write(f"第{xue}靴\n")
        while 1 > 0:
            print(f"------开始第{n}局投注------")
            fn.write(f"开始第{n}局投注\n")
            # main
            tou_zhu = input("请输入投注参数：")
            fn.write(f"投注明细：{tou_zhu}\n")
            a = list(tou_zhu.split(' '))
            z_list = []
            x_list = []
            for i in a:
                if re.match(r'^z', i):
                    z_list.append(int(i.split('z')[1]))
                if re.match(r'^x', i):
                    x_list.append(int(i.split('x')[1]))
            z_num = len(z_list)
            x_num = len(x_list)
            z_sum = sum(z_list)
            x_sum = sum(x_list)
            print(f"庄 投注人数 {z_num}")
            print(f"闲 投注人数 {x_num}")
            print(f"庄 投注总额 {z_sum}")
            print(f"闲 投注总额 {x_sum}")
            r = 'h'
            if z_sum > x_sum:
                r = 'x'
            if x_sum > z_sum:
                r = 'z'
            print(f"预测投注结果：{r}")

            y = input("下注 z|x：")
            rr = input("实际投注结果：")
            if y == rr:
                w += 10
            else:
                w -= 10
            fn.write(f"投注统计：庄 {z_num} {z_sum} | 闲 {x_num} {x_sum} \n")
            fn.write(f"投注结果统计：预测投注结果：{r} | 实际投注结果：{rr} \n")
            # main

            print(f"我的余额：{w},我的盈利：{w - 500}")
            n += 1


if __name__ == '__main__':
    d = time.strftime("%Y-%m-%d", time.localtime())
    main()
