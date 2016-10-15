#encoding:utf-8
import os
import sys
import time
import re


#使用之前，确保手机开启usb调试模式并连上电脑配置好adb命令环境变量。基于python2.7。
#################################################################
#########              LppzApp_Monkey测试               #########
#################################################################

packageName="com.lppz.mobile.android.outsale"     #设置待测app的包名

logdir=r"E:\jenkins"                              #设置log的路径
remote_path=r"E:\jenkins\error"                   #设置errorlog 的路径

os.system('mkdir E:\jenkins\error')									#创建文件夹目录
os.system('adb shell cat /system/build.prop >E:\jenkins\phone.txt')   #重定向手机里的build.prop文件到本机另存为phone.txt。

file = r"E:\jenkins\phone.txt" #指定phone.txt文件的路径

def get_phone_info(filepath):   #定义一个方法 传入一个命令，返回手机里的三个信息。分别是 版本 机型 品牌
    f = open(filepath,"r")      #打开这个文件
    lines = f.readlines()       #一行行的读取
    for line in lines:          #for循环 每次循环读一行内容，每行内容按“=” 分割成两个部分。
        line=line.split('=')
        if (line[0]=='ro.build.version.release'):
            version = line[1]
        if (line[0]=='ro.product.model'):
            model = line[1]
        if (line[0]=='ro.product.brand'):              #判断这行前面内容为型号时。就把后面的内容（值）传给你的变量。
            brand = line[1]
    return version,model,brand                        #返回这三个值


version,model,brand=get_phone_info(file)         #调用方法 给这三个变量赋值

print version,model,brand       #打印出来到控制台
os.remove(file)

print"关闭手机中所有已经打开的app"
os.popen("adb shell am force-stop %s"%(packageName))

print "使用logcat清空手机中的log"
os.popen("adb logcat -c")

print"暂停2秒..."
print "please waite..."
time.sleep(2)

now1 = time.strftime('%Y-%m-%d-%H_%M_%S', time.localtime(time.time()))   #取本机时间并格式化

print"开执行Monkey命令"
monkeylogname=logdir+"\\"+now1+"monkey.log"    #设置monkey日志保存路径
print "日志保存于："+monkeylogname                            #打印路径
monkey_cmd="adb shell monkey -p %s -s 500 --ignore-timeouts --monitor-native-crashes -v -v --throttle 30 10000 >>%s" %(packageName,monkeylogname)
os.popen(monkey_cmd)   

print"手机截屏"
os.popen("adb shell screencap -p /sdcard/monkey_run.png")

print"拷贝截屏图片至电脑"
screencut_cmd="adb pull /sdcard/monkey_run.png %s" %(logdir)
os.popen(screencut_cmd)

print "修改图片文件名"
oldname=logdir+"\\"+r"monkey_run.png"
if (os.path.exists(oldname)):
    print "文件存在，立马改名"
    newname=logdir+"\\"+now1+r"monkey.png"
    os.rename(oldname, newname)
else:
    print "文件不存在"


print"使用Logcat导出日志"

logcatname=logdir+"\\"+now1+r"logcat.log"
logcat_cmd="adb logcat -d >%s" %(logcatname)
os.popen(logcat_cmd)

print"导出traces日志"

tracesname=logdir+"\\"+now1+r"traces.log"
trace_cmd="adb shell cat /data/anr/traces.txt>%s" %(tracesname)
os.popen(trace_cmd)

######################
#生成error log
######################


#定义以下常见的闪退异常

NullPointer="java.lang.NullPointerException"
IllegalState="java.lang.IllegalStateException"
IllegalArgument="java.lang.IllegalArgumentException"
ArrayIndexOutOfBounds="java.lang.ArrayIndexOutOfBoundsException"
RuntimeException="java.lang.RuntimeException"
SecurityException="java.lang.SecurityException"
IndexOutOfBounds="java.lang.IndexOutOfBoundsException"
ClassCast="java.lang.ClassCastException"


def geterror():       #从logcat 手机运行日志中找出包含以上异常信息的行 输出前25行 并写入errlog
    f = open(logcatname,"r")     
    lines = f.readlines()
    #errfile="%s+now1+\error.log" %(remote_path)
    errfile = remote_path+"\\"+now1+"error.log" 

	
    #if (os.path.exists(errfile)):
     #   os.remove(errfile)
    fr = open(errfile,"a")
    fr.write(version)
    fr.write("\n")
    fr.write(model)
    fr.write("\n")
    fr.write(brand)
    fr.write("\n")
    fr.write(now1)
    fr.write("\n")
    count=0
    quchong_list = []
    for line in lines:
        if ( re.findall(NullPointer,line) or re.findall(IllegalState,line) or re.findall(IllegalArgument,line) or re.findall(ArrayIndexOutOfBounds,line) or re.findall(RuntimeException,line) or re.findall(SecurityException,line) or re.findall(IndexOutOfBounds,line)or re.findall(ClassCast,line)):
                a=lines.index(line)
                count +=1
                quchong_list.append(re.split(r'E ', line)[1])
                for var in range(a,a+25):
                    print lines[var]
                    fr.write(lines[var])				
                fr.write("\n")
    f.close()
    fr.close()
    return count,quchong_list


number,quchong_list=geterror()

quchong = list(set(quchong_list))

if(number>=1):
	print("程序崩溃了...")
	print "共抓到"+str(number)+"个错误!"
	for n in quchong:
		print n
	print "去重后只有以上"+(str)(len(quchong))+"个错误!"
sys.exit(1)