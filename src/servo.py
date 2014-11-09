from telescope_beta import telescope

t=telescope("10.130.133.12")

f=open("servo.json",'r')

servoDict = eval(f.read())

t.comSERVO( 1, servoDict)
t.request("CON 1")
