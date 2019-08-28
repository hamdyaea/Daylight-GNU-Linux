# Developer : Hamdy Abou El Anein
from tkinter import *
import os
import urllib.request

hostname = "google.com"

class Application(Frame):
	def __init__(self,parent):
		Frame.__init__(self)
		self.parent = parent
		self.etat = Label(self, text='',font='Times 28 italic bold')
		self.etat.grid(row=0, column=0, columnspan=4, sticky=NSEW)
 
		self.lab_iface = Label(self, text='Interfaces:',font='Times',underline=0)
		self.lab_iface.grid(row=1,column=0,sticky=NSEW)
 
		self.iface = Text(self, font='Times 10')
		self.iface.grid(row=2, column=0, sticky=NSEW)
 
		self.lab_ping = Label(self, text='Ping:',font='Times',underline=0)
		self.lab_ping.grid(row=1,column=2,sticky=NSEW)
 
		self.ping = Text(self, font='Times',state='disabled')
		self.ping.grid(row=2, column=1, columnspan=3, sticky=NSEW)
 
		self.recharger = Button(self, text='Recharger', font='Times', command=self.checkIface)
		self.recharger.grid(row=3, column=0, sticky=NSEW)
 
		self.quitter = Button(self, text='Quitter', font='Times', command=self.leave)
		self.quitter.grid(row=3, column=1, columnspan=3,sticky=NSEW)
 
		self.checkIface()
 
	def checkIface(self):
		self.iface.config(state='normal')
		self.iface.delete(1.0,END)
		self.listing = os.popen('ifconfig', 'r').read()
		self.iface.insert(END, self.listing)
		self.iface.config(state='disabled')
		self.checkInternet()
 
	def checkInternet(self):
		try:
			urllib.request.urlopen('http://www.google.com')
			self.etat.config(text='Connexion internet active')
			self.checkPing()
		except:
			self.etat.config(text='Connexion internet inactive')
			self.ping.config(state='normal')
			self.ping.delete(1.0,END)
			self.ping.insert(END, 'Ping impossible...')
			self.ping.config(state='disabled')
 
	def checkPing(self):
		self.ping.config(state='normal')
		self.ping.delete(1.0,END)
		c = 3
		while c != 0:
			self.pingPacket = os.popen("ping -c 1 "  + hostname).read()
			self.ping.insert(END, self.pingPacket+'\n')
			self.parent.after(1,self.parent.update())
			c = c-1
 
		self.ping.config(state='disabled')
 
	def leave(self):
		quit()
 
if __name__ == '__main__':
	fen = Tk()
	fen.title('Connexion Internet')
	fen.resizable(False,False)
 
	app = Application(fen)
	app.grid(row=0, column=0, sticky=NSEW)
 
	fen.mainloop()
