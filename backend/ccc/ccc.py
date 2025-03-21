# coding: utf-8

import re


def main():
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
    rr = input("实际投注结果：")

    fn.write(f"投注统计：庄 {z_num} {z_sum} | 闲 {x_num} {x_sum} \n")
    fn.write(f"投注结果统计：预测投注结果：{r} | 实际投注结果：{rr} \n")


if __name__ == '__main__':
    xue = input("输入靴号：")
    with open(f"bjl_{xue}.txt", "a+") as fn:
        fn.write(f"第{xue}靴\n")
        n = 1
        while 1 > 0:
            print(f"------开始第{n}局投注------")
            fn.write(f"开始第{n}局投注\n")
            main()
            n += 1
