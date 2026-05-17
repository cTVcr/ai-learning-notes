#!/usr/bin/env python3
# -*- coding: utf-8 -*-

x=10
s="hi"
print('I\'m ok.')
print('hello vs code')
# print(x+s)
print('I\'m learning\nPython.')
print('''line1
line2
line3''')
# 基础语法学习
True and True
Anser=True
print(Anser)
a='abc'
print(a)
a=124
print(a)
b=a
a='233'
print(b)

# 普通除法 结果都是浮点数
print(10/3)
print(9/3)
# 地板除法 结果都是整数
print(10//3)
print(9//3)

# 字符串
print('我是中国人使用的是中文string，然后使用的是unincode编码 在python里面 ，然后支持多语言')
print(chr(25991))
print(ord('中'))

print('ABC'.encode('ascii'))
print(b'ABC'.decode('ascii'))
print('中文'.encode('utf-8'))
print(b'\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8'))
print(b'\xe4\xb8\xad\xff'.decode('utf-8',errors='ignore'))
# print(b'\xe4\xb8\xad\xff'.decode('utf-8'))
# print('中文'.encode('ascii'))

# len() is used
print(len('ABCDEF'))
print(len('中文'))
print(len(b'ABCDEF'))
print(len('中文'.encode('utf-8')))

print('hello,%s hhh' % 'world')
print('Hi,%s,you have $%d.'%('liming',10000))
print('%2d-%02d'%(3,1))
print('%.2f'%3.1415926)
print('Age:%s. Gender:%s' %(25,True))
print('growth rate:%d %%' %7)
print('Hello,{0},成绩提升了{1:.1f}%'.format('明',17.35))
r=2.5
s=3.14*r**2
print(f'The area of a circle with radius {r} is {s:.2f}')
s1=72
s2=85
r=(s2-s1)/s1
print('提升%.1f%%'%(r*100))

classmates=['mechtine','bob','tracy']
print(classmates)
print(len(classmates))
classmates.append('sssa')
print(classmates)

classmates.insert(1,'jack')
print(classmates)

classmates.pop()
print(classmates)

classmates.pop(1)
print(classmates)
L=["aappp",'aaappp',classmates,12213,]
print(L)
print(L[2][1])

classmet=('bob','tracy','me')
t=(1,2)
print(t)
# t.append(1)
# print(t)
t=()
print(t)

t=(1,)
print(t)
t=(1)
print(t)

age=4
if age >= 18:
    print('your age is',age)
    print('adult')
elif age>=6:
    print('teenager')
else:
    print('you age is',age)
    print('kid')

if 1:
    print(True)
# s=input('birth:')
birth=int(s)
if birth< 2000:
    print('00前')
else:
    print('00后')

# 模式匹配

score='B'
match score:
    case 'A':
        print('scpre is A.')
    case 'B':
        print('mid')
    case 'C':
        print('low')
    case _:
        print('not sure')


