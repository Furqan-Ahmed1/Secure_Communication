from PyQt5 import QtCore, QtGui, QtWidgets
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os
import pyaes, pbkdf2, binascii, os, secrets
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import time
import hashlib
BLOCK_SIZE = 32 # Bytes



        # 2.adds the status and message event listeners
class  MySubscribeCallback(SubscribeCallback):
    # def __init__(self):
    #     self.c2 = self.Ui_chatroom(self)

    def message(self, pubnub, message):
        # print("In Message Handler..")
        ciphertext = message.message.encode("latin-1")
        # print('Encrypted:', binascii.hexlify(ciphertext))

        key_AES = pbkdf2.PBKDF2(pnconfig.secret_key, Salt).read(32)
        key_DES = pbkdf2.PBKDF2(pnconfig.secret_key, Salt).read(8)
            
        #DECRYPTING WITH DES HERE
        des = DES.new(key_DES, DES.MODE_ECB)
        decrypted = des.decrypt(ciphertext)
        decrypted = unpad(decrypted, BLOCK_SIZE)
        # print(decrypted)

        #DECRYPTING WITH AES HERE
        aes = pyaes.AESModeOfOperationCTR(key_AES, pyaes.Counter(iv))
        decrypted = str(aes.decrypt(decrypted))
        print(decrypted[2:-1])
        ui.chatlist.addItem(decrypted[2:-1])

    def signal(self, pubnub, signal):
        # print("In Signal Handler..")
        if(signal.message[0:4] == "Salt"):
            # print("initializing Salt")
            # print("MSG:"+signal.message)
            global Salt 
            Salt = bytes(signal.message[7:-1], 'ascii')
        if(signal.message[0:2] == "iv"):
            # print("initializing iv")
            # print("MSG:"+signal.message)
            global iv
            iv = int(signal.message[3:])

class Ui_chatroom(object):
    def setupUi(self, chatroom):
        chatroom.setObjectName("chatroom")
        chatroom.resize(675, 495)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../Downloads/chat-2639493-2187526.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        chatroom.setWindowIcon(icon)
        chatroom.setWhatsThis("")
        chatroom.setAccessibleName("")
        chatroom.setAutoFillBackground(False)
        chatroom.setModal(False)
        self.title = QtWidgets.QLabel(chatroom)
        self.title.setGeometry(QtCore.QRect(200, 10, 261, 20))
        self.title.setObjectName("title")
        self.chatlist = QtWidgets.QListWidget(chatroom)
        self.chatlist.setGeometry(QtCore.QRect(20, 50, 631, 361))
        self.chatlist.setObjectName("chatlist")
        self.sendbtn = QtWidgets.QPushButton(chatroom)
        self.sendbtn.setGeometry(QtCore.QRect(600, 430, 51, 51))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.sendbtn.setFont(font)
        self.sendbtn.setDefault(True)
        self.sendbtn.setFlat(False)
        self.sendbtn.setObjectName("sendbtn")
        self.textbox = QtWidgets.QLineEdit(chatroom)
        self.textbox.setGeometry(QtCore.QRect(20, 430, 571, 51))
        self.textbox.setObjectName("textbox")

        self.textbox.setPlaceholderText("Enter Your Chat Name:  ")
        # self.textbox.editingFinished.connect(self.enterName)
        
        
        self.sendbtn.clicked.connect(self.enterMsg)

        self.sendbtn.clicked.connect(self.enterName)

        self.retranslateUi(chatroom)
        QtCore.QMetaObject.connectSlotsByName(chatroom)
        

    def enterName(self):
            global count
            if(count==0):
                count+=1
                global name
                name = self.textbox.text()
                print("name: ", name)
                self.textbox.clear()
                self.textbox.setPlaceholderText("Type Message Here:  ")

    def saveAttemptsStatus(self):
        filename= "testfile.txt"
        file = open(os.path.join("Backup",filename),"w")
        itemsTextList =  [str(self.chatlist.item(i).text()) for i in range(self.chatlist.count())]
        for item in itemsTextList:
            file.write(item)
            file.write("\n")
            print(item)   

        file.close()
        

    def enterMsg(self):
            # print("Enter or SendBtn Pressed")
            global count
            if(count==1):
                msg = self.textbox.text()
                print(msg)
                self.textbox.clear()

                msg = name +": " +msg

                if msg == name +": " +'exit':
                    filename= "testfile.txt"
                    self.saveAttemptsStatus()
                    h  = hashlib.sha256()
                    b  = bytearray(128*1024)
                    mv = memoryview(b)
                    with open(os.path.join("Backup",filename), 'rb', buffering=0) as f:
                        for n in iter(lambda : f.readinto(mv), 0):
                            h.update(mv[:n])
                    file_hash = h.hexdigest()

                    os.rename(os.path.join("Backup",filename),os.path.join("Backup",file_hash))
                    os._exit(1)
                if msg == name +": " +'salt': print(Salt)

                else: 
                    key_AES = pbkdf2.PBKDF2(pnconfig.secret_key, Salt).read(32)
                    key_DES = pbkdf2.PBKDF2(pnconfig.secret_key, Salt).read(8)
                    
                    # print(key_AES)
                    # print(key_DES)
                    # print('AES encryption key:', binascii.hexlify(key))

                    #ENCRYPTING WITH AES HERE
                    aes = pyaes.AESModeOfOperationCTR(key_AES, pyaes.Counter(iv))
                    ciphertext = aes.encrypt(msg)
                    # print("AES ENCRYPTED: ", ciphertext)

                    #ENCRYPTING WITH DES HERE
                    des = DES.new(key_DES, DES.MODE_ECB)
                    ciphertext = des.encrypt(pad(ciphertext,BLOCK_SIZE))
                    # print("DES ENCRYPTED: ", ciphertext)

                    # 4.publishes a message
                    pubnub.publish().channel("chan-1").message(ciphertext.decode("latin-1")).pn_async(my_publish_callback)

    def retranslateUi(self, chatroom):
        _translate = QtCore.QCoreApplication.translate
        chatroom.setWindowTitle(_translate("chatroom", "Chat Room"))
        self.title.setText(_translate("chatroom", ".........  END TO END DOUBLE ENCRYPTED  ........."))
        self.sendbtn.setText(_translate("chatroom", "SEND"))




if __name__ == "__main__":
    
    import sys

    app = QtWidgets.QApplication(sys.argv)
    chatroom = QtWidgets.QDialog()
    ui = Ui_chatroom()
    ui.setupUi(chatroom)    


    def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
        if not status.is_error():
            pass

    # 1.configures a PubNub connection
    global count
    count = 0
    pnconfig = PNConfiguration()
    pnconfig.publish_key = '--Enter your publish key here--'
    pnconfig.subscribe_key = '--Enter your subscribe key here--'
    pnconfig.ssl = True
    pnconfig.secret_key = 's3cr3t*c0d3' #password 
    pubnub = PubNub(pnconfig)
    
    global Salt
    Salt = os.urandom(8)

    global iv
    iv = secrets.randbits(128)

    pubnub.add_listener(MySubscribeCallback())

    # 3.subscribes to a channel
    pubnub.subscribe().channels("chan-1").execute()
    pubnub.signal().channel("chan-1").message("Salt:" +str(Salt)).sync()
    pubnub.signal().channel("chan-1").message("iv:" +str(iv)).sync()
    print("Wait while Encryption Keys are exchanging..")
    time.sleep(5)

    chatroom.show()
    sys.exit(app.exec_())

