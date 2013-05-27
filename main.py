#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import socket
import libssh2
from PySide import QtGui, QtCore
import connection as con

class Graphics(QtGui.QWidget):
    
    def __init__(self):
        super(Graphics, self).__init__()
        self.initUI()
        
    #---- metoda obsługująca główny interfejs graficzny
    def initUI(self):
        #----------------------------------
        portInfo = QtGui.QLabel('Port')
        self.portEnter = QtGui.QLineEdit()
        self.portEnter.setFixedSize(50, 30)
        self.portEnter.setText('22')
        
        addressInfo = QtGui.QLabel('Address')
        self.addressEnter = QtGui.QLineEdit()
        self.addressEnter.setFixedSize(200, 30)
        self.addressEnter.setText('10.0.0.100')
        
        sideLabel = QtGui.QLabel()
        sideLabel.setFixedWidth(40)
        
        port_address_layout = QtGui.QHBoxLayout()
        port_address_layout.addWidget(sideLabel)
        port_address_layout.addWidget(portInfo)
        port_address_layout.addWidget(self.portEnter)
        port_address_layout.addWidget(sideLabel)
        port_address_layout.addWidget(addressInfo)
        port_address_layout.addWidget(self.addressEnter)
        port_address_layout.addWidget(sideLabel)
        #-----------------------------------------------
        
        # connect button layout
        self.connectButton = QtGui.QPushButton("Connect")
        self.connectButton.setFixedWidth(350)
        
        self.connectButton.clicked.connect(self.connect)
      
        
        connectButtonLayout = QtGui.QHBoxLayout()
        connectButtonLayout.addWidget(self.connectButton)
        
        # status
        self.statusLabel = QtGui.QLabel()
        self.statusLabel.setText('Idle')
        
        statusLayout = QtGui.QHBoxLayout()
        statusLayout.addWidget(self.statusLabel)
        
        # pomocniczy pionowy layout
        enterAddressInfo = QtGui.QLabel()
        enterAddressInfo.setText("Enter command")
        enterAddressInfo.setFixedWidth(300)
        
        self.enterAddress = QtGui.QLineEdit()
        self.enterAddress.setFixedWidth(500)
      
        
        littleVbox = QtGui.QVBoxLayout()
        littleVbox.addWidget(self.statusLabel)
        littleVbox.addWidget(enterAddressInfo)
        littleVbox.addWidget(self.enterAddress)

        # exec button layout
        execButton = QtGui.QPushButton("Execute")
        execButton.setFixedWidth(350)
        execButton.clicked.connect(self.getCommand)
        
        execButtonLayout = QtGui.QHBoxLayout()
        execButtonLayout.addWidget(execButton)
        
        # pomocniczy, centrujący poziomy layout
        lrSide = QtGui.QLabel()
        lrSide.setFixedWidth(10)
        
        littleHbox = QtGui.QHBoxLayout()
        littleHbox.addWidget(lrSide)
        littleHbox.addLayout(littleVbox)  
        littleHbox.addWidget(lrSide)
       
        # odstępy góra-dół layout
        vSpacingMenu = QtGui.QLabel()
        vSpacingMenu.setFixedHeight(10)
        vSpacingTop = QtGui.QLabel()
        vSpacingTop.setFixedHeight(30)
        vSpacingBottom = QtGui.QLabel()
        vSpacingBottom.setFixedHeight(50)
        # odstępy lewo-prawo ; centering layout
        sideLabel1 = QtGui.QLabel()
        sideLabel1.setFixedWidth(25)

        sideSpace = QtGui.QHBoxLayout()
        sideSpace.addWidget(sideLabel1)
        
        #---- menubar
        # actions
        exitAction = QtGui.QAction(QtGui.QIcon(''), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        newConfigAction = QtGui.QAction(QtGui.QIcon(''), '&New config file', self)
        newConfigAction.triggered.connect(self.newConfig)
        
        openConfigAction = QtGui.QAction(QtGui.QIcon(''), '&Open config file', self)
        openConfigAction.triggered.connect(self.openConfig)
        # menubar
        menubar = QtGui.QMenuBar()
        # zakładka main
        mainMenu = menubar.addMenu('&Main')
        
        configurationMenu = mainMenu.addMenu('Configuration')
        configurationMenu.addAction(newConfigAction)
        configurationMenu.addAction(openConfigAction)
        
        mainMenu.addAction(exitAction)
        
        # zakładka info
        infoMenu = menubar.addMenu('&Info')
        
        # menubar layout
        menuLayout = QtGui.QHBoxLayout()
        menuLayout.addWidget(menubar)
        #---- menubar end
        
        #---- center layout
        self.commandLabel = QtGui.QLabel()

        self.infoText = QtGui.QTextBrowser()
#        self.infoText = QtGui.QTextEdit()
        self.infoText.setFixedSize(550, 500)
        
        centerVboxLayout = QtGui.QVBoxLayout()
        centerVboxLayout.addLayout(port_address_layout)
        centerVboxLayout.addLayout(statusLayout)
        centerVboxLayout.addLayout(connectButtonLayout)
        centerVboxLayout.addWidget(vSpacingTop)
        centerVboxLayout.addLayout(littleHbox)
        centerVboxLayout.addLayout(execButtonLayout)
        centerVboxLayout.addWidget(self.commandLabel)
        centerVboxLayout.addWidget(self.infoText)
        centerVboxLayout.addWidget(vSpacingBottom)
        #---- main layout
        main = QtGui.QHBoxLayout()
        main.addLayout(sideSpace)
        main.addLayout(centerVboxLayout)
        main.addLayout(sideSpace)
        
        allLayouts = QtGui.QVBoxLayout()
        allLayouts.addLayout(menuLayout)
        allLayouts.addWidget(vSpacingMenu)
        allLayouts.addLayout(main)
        
        self.setLayout(allLayouts)
        self.setGeometry(200, 200, 600, 600)
        self.setWindowTitle("SSH Client")
        self.show() 

#-----------------------------------#
#------------ Metody ---------------#   
#-----------------------------------#
  
    #---- grupa metod obsługująca wybór sposobu autentykacji
    #---- i ich wykorzystania (jednorazowegó lub wielokrotnego)
    def newConfig(self):        
        passwordButton = QtGui.QPushButton('Password')
        enterKeyButton = QtGui.QPushButton('Key')
        openKeyButton = QtGui.QPushButton('Key from file')
        
        message = QtGui.QMessageBox()
        message.setText('Select the way of authentication')
        message.addButton(passwordButton, message.YesRole)
        message.addButton(enterKeyButton, message.NoRole)
#        message.addButton(openKeyButton, message.ApplyRole)
        message.exec_()
        response = message.clickedButton().text()
        
        if response == 'Password':
            self.enterPassword()
        elif response == 'Key':
            self.enterKey()
        elif response == 'Key from file':
            self.openKP()
    
    def openConfig(self):
        openPasswordButton = QtGui.QPushButton('Open password')
        openKeyButton = QtGui.QPushButton('Open key')
        
        message = QtGui.QMessageBox()
        message.addButton(openPasswordButton, message.YesRole)
        message.addButton(openKeyButton, message.NoRole)
        message.exec_()
        response = message.clickedButton().text()
        
        if response == 'Open password':
            #otwórz plika bazy i wyciagnij hasło 
            pass
        else:
            #otwórz plik bazy i wyciagnij klucz
            pass
        
    def enterPassword(self):
        enterUser = QtGui.QLineEdit()
        enterName = QtGui.QLineEdit()
        enterConfName = QtGui.QInputDialog()

        user = enterConfName.getText(self, "Enter user name", \
                "Enter user name", enterUser.Normal)
        name = enterConfName.getText(self, "Enter password", \
                "Enter password", enterName.Password)
        userName = str(user)[0]
        configName = str(name[0])
        self.selectUsage('password', userName, configName)
        
    def enterKey(self):
        enterName = QtGui.QLineEdit()
        enterConfName = QtGui.QInputDialog()

        name = enterConfName.getText(self, "New config file", \
                "Enter new config filename", enterName.Normal)
        configName = str(name[0])
        self.selectUsage('key', configName)

    def selectUsage(self, auth, user, info):
        oneTimeButton = QtGui.QPushButton('One time usage')
        saveButton = QtGui.QPushButton('Save into file')
        
        message = QtGui.QMessageBox()
        message.setText('Select the way of authentication')
        message.addButton(oneTimeButton, message.YesRole)
        message.addButton(saveButton, message.NoRole)
        message.exec_()
        response = message.clickedButton().text()
        
        if auth == 'password':
            if response == 'One time usage':
                self.oneTimeUsagePassword(user, info)
            else:
                self.saveIntoFile(user, info)
        else:
            if response == 'One time usage':
                self.oneTimeUsageKey(user, info)
            else:
                self.saveIntoFile(user, info)
        
    def openKey(self):
        pass
        
    def oneTimeUsagePassword(self, user, password):
        self.mode = 0
        
    def saveIntoFile(self, user, password):
        print "save password", password
        saveFileDialog = QtGui.QFileDialog.getSaveFileName(self, "Save config", "/home")
        print str(saveFileDialog)
        self.mode = 0
        
    def oneTimeUsageKey(self, user, key):
        print key
        self.mode = 1
    #----
    
    #---- grupa metod odpowiedzialna za komunikację SSH ze zdalnym hostem,
    #---- wysyłanie, pobieranie listingu i wyswietlanie go w głównym oknie    
    def getCommand(self):
#        self.infoText.clear()
        command = self.enterAddress.text()
        self.commandLabel.setText("Listing for %s:" % command)
        channel = self.session.channel()
        channel.execute(command)
        
        self.infoText.append\
        ('*** Listing for %s ***' % command)
        
        windowSize = 2048
        currentSize = len(channel.read(windowSize))
        while True:
            if currentSize < windowSize \
            and currentSize > windowSize/2:
                break
            else:
                windowSize = windowSize / 2
        print windowSize
        
        while channel.read(windowSize):
#            buff += channel.read(1024)
#            self.infoText.append(channel.read(1024))
            self.setInfo(channel.read(windowSize))
#            channel.flush()
#            self.setInfo(buff)
#            self.setInfo(channel.read(1024))
        
        self.enterAddress.clear()
    
    def setInfo(self, info):
        self.infoText.append(info)
#        listing = con.execCommand(str(command))
#        self.commandLabel.setText("Listing for %s:" % command)
#        self.infoText.setText(listing)
#        self.enterAddress.clear()
    #----
    #----
    
    #---- grupa metod odpowiedzialna za nawiązywanie połączenia
    #---- ze zdalnym hostem oraz ustawianie statusu połączenia
    def connect(self):
        address = self.addressEnter.text()
        port = self.portEnter.text()
        
        if self.connectButton.text() == "Connect":
            self.status = con.connect(address, port)[0]
            self.session = con.connect(address, port)[1]
            self.setStatus()
            self.connectButton.setText("Disconnect")
        else:
            self.disconnect()
            
    def disconnect(self):
        self.setStatus()
        self.connectButton.setText("Connect")
    
    def setStatus(self):
        if self.status == 1:
            self.status = "Connected"
        else:
            self.status = "Disconnected"
        self.statusLabel.setText(str(self.status))
    #----
    #----
    
def main():
    app = QtGui.QApplication(sys.argv)
    grph = Graphics()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main() 
        
        