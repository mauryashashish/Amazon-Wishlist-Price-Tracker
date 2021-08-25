#! python3

# importing libraries and modules
import requests
import bs4
import lxml
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# creating a Bag/wishlist to store the products, check price and send mail
class Wishlist:
	
	def __init__ (self):
		
		self.itemList = {}
		self.itemPrice = {}

	
	def getURL(self, url):
		# most of the amazon standard identification number starts with "B0"
		asin_id = url.find("B0")
		if asin_id == -1:
			return -1
		asin = url[asin_id:asin_id+10]
		return (asin, url[:asin_id+10])

	
	def addItem (self, url, price):
		
		if self.getURL(url) == -1:
			print("INVALID REQUEST\n")
		else:
			asin, asinurl = self.getURL(url)
			self.itemPrice.update({asin: price})
			self.itemList.update({asin: asinurl})
			print("The Product was added to the Wishlist!")

	
	def removeItem (self, url):
		
		if self.getURL(url) == -1:
			print("INVALID REQUEST\n")
		else:
			asin, asinurl = self.getURL(url)
			try:
				del self.itemList[asin]
			except:
				print("INVALID REQUEST")

			try:
				del self.itemPrice[asin]
				print("The Product was removed from the Wishlist!")
			except:
				print("INVALID REQUEST")


	def getDetails (self, url):

		try:
			res = requests.get(url)
		except Exception as e:
			# print(e)
			return -1
		# here we can also use html.parser but lxml is faster
		# lxml does not come with python3 by default
		soup = bs4.BeautifulSoup(res.text,'lxml')
		soup.encode('utf-8')

		try:
			title = soup.find(id= "productTitle").getText().strip()
			price = float(soup.find(id = "priceblock_ourprice").getText().replace(',', '').replace('₹', '').replace(' ', '').strip())
		except Exception as e:
			# print(e)
			return -1

		return (title, price)

	
	def sendMail (self, url, title, price):
		
		sender_email = "sender@gmail.com"
		password = "password"

		receiver_email = "receiver@gmail.com"
		
		context = ssl.create_default_context()

		message = MIMEMultipart("alternative")
		message["Subject"] = "Check out the price of this product from your Wishlist"
		message["From"] = sender_email
		message["To"] = receiver_email

		# Plain text version of message
		text = """\
		Hey!

		Shop your favourite product on affordable price.

		{title} is now available at INR {price}.

		Check it out on: {link}
		""".format(title = title, price = price, link = url)

		# HTML version of message
		html = """\
		<html>
			<body><p>Hey!<br><br>Shop your favourite product on affordable price.<br><br>{title} is now available at INR {price}.<br><br>Check it out on: <a href={link}>here</a></p></body>
		</html>
		""".format(title = title, price = price, link = url)

		# Turn these into plain text/html MIMEText objects
		part1 = MIMEText(text, "plain")
		part2 = MIMEText(html, "html")

		# Add HTML/plain-text parts to MIMEMultipart message
		# The email client will try to render the last part first
		message.attach(part1)
		message.attach(part2)

		# Sending HTML content email through TLS encryption
		try:
			server = smtplib.SMTP("smtp.gmail.com", 587)
			server.starttls(context = context)
			server.login(sender_email, password)
			server.sendmail(sender_email, receiver_email, message.as_string())
		except Exception as e:
			print(e)
		finally:
			server.quit()

	
	def checkPrice(self):
		
		for item in self.itemList:
			
			url = self.itemList[item]
			price = self.itemPrice[item]

			try:
				title, cur_price = self.getDetails(url)
			except Exception as e:
				# print(e)
				print("Product details are currently unavailble")
				continue

			if cur_price <= price:
				self.sendMail(url, title, cur_price)
				print("Mail sent for {title} at current price of INR {cur_price}".format(title = title, cur_price = cur_price))
			else:
				print("The current price of {title} is still at INR {cur_price}".format(title = title, cur_price = cur_price))



# Below is the main function

#create an instance of the Wishlist class
bag = Wishlist()

# add Items to the wishlist
bag.addItem("https://www.amazon.in/dp/B092J39VJC/ref=s9_acsd_al_bw_c2_x_2_t?pf_rd_m=A1K21FY43GMZF8&pf_rd_s=merchandised-search-4&pf_rd_r=K844RZ0X3PEDVJCEAMTF&pf_rd_t=101&pf_rd_p=48c4b04e-a3bc-45ee-b57e-03d8942c7c53&pf_rd_i=20656599031", 20000)
bag.addItem("https://www.amazon.in/dp/B08VB57558/ref=s9_acsd_al_bw_c2_x_0_t?pf_rd_m=A1K21FY43GMZF8&pf_rd_s=merchandised-search-6&pf_rd_r=K844RZ0X3PEDVJCEAMTF&pf_rd_t=101&pf_rd_p=21419d67-a09e-499d-aa17-67fb517eb3f6&pf_rd_i=20656599031", 50000)
bag.addItem("https://www.amazon.in/ASUS-i7-10700-Graphics-Keyboard-G15CK-IN030T/dp/B08SX424XD/?_encoding=UTF8&pd_rd_w=FYWEz&pf_rd_p=730090a5-d1cb-4d65-a97c-9881819a53f1&pf_rd_r=KMCTW8PQACPKYG9ZCRR8&pd_rd_r=ce5b2971-59e6-4267-822a-2e1bfee35f9b&pd_rd_wg=AyeQl&ref_=pd_gw_ci_mcx_mr_hp_atf_m", 160000)
bag.addItem("https://www.amazon.in/dp/B091FH823X/ref=s9_acsd_al_bw_c2_x_3_t?pf_rd_m=A1K21FY43GMZF8&pf_rd_s=merchandised-search-6&pf_rd_r=ZM4SCB50CCC033JAA36K&pf_rd_t=101&pf_rd_p=b5ba1f27-71f8-4f22-b4e4-75bffae66a9a&pf_rd_i=26297682031", 75000)


# this loop runs the checkPrice function once every 30 seconds
while True:
	print(time.ctime())
	bag.checkPrice()
	time.sleep(30)

