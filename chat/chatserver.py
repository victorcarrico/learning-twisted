from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class ChatProtocol(LineReceiver):
	def __init__(self, factory):
		self.factory = factory
		self.name = None
		self.state = "REGISTER"
	
	def connectionMade(self):
		self.sendLine("Qual seu nome?")
	
	def connectionLost(self, reason):
		if self.name in self.factory.users:
			del self.factory.users[self.name]
			self.broadcastMessage("%s deixou o canal." % (self.name,))
	
	def lineReceived(self, line):
		if self.state == "REGISTER":
			self.handle_REGISTER(line)
		else:
			self.line_TYPE(line)

	def line_TYPE(self,line):
		if line[0] == '\\':
			return self.handle_CMD(line)
		return self.handle_CHAT(line)
	
	def handle_REGISTER(self, name):
		if name in self.factory.users:
			self.sendLine("Nome de usuario ja existe, escolha outro.")
			return
		
		self.sendLine("Bem-vindo ao Bate-Papo Tru, %s!" % (name,))
		self.broadcastMessage("%s entrou no canal." % (name,))
		self.name = name
		self.factory.users[name] = self
		self.state = "CHAT"
	
	def handle_CHAT(self, message):
		message = "<%s> %s" % (self.name, message)
		self.broadcastMessage(message)
	
	def broadcastMessage(self, message):
		for name, protocol in self.factory.users.iteritems():
			if protocol != self:
				protocol.sendLine(message)

	def handle_CMD(self,message):
		if message[1:] == 'users':
			for name, protocol in self.factory.users.iteritems():
				self.sendLine(name)
		self.handle_CHAT(message)


class ChatFactory(Factory):
	def __init__(self):
		self.users = {}

	def buildProtocol(self, addr):
		return ChatProtocol(self)

reactor.listenTCP(22, ChatFactory())
reactor.run()
