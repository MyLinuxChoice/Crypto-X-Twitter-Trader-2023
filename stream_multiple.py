# Another method using streaming (mitigates the wait on rate limit issue)
import tweepy
import time,getpip
import json
import sys
from datetime import datetime
from tweepy import Stream
from tweepy.streaming import StreamListener
from check_exchange import *
import re
import threading
import traceback

# Listener class
class Listener(StreamListener):
	def __init__(self, users, user_ids, sell_coin, hold_times, buy_volume, simulate, exchange, exchange_data, buy_coin=None, log_file=None, full_ex=True):
		super(Listener,self).__init__()

		# Define variables for the class when listener is created
		self.users = users
		self.user_ids = user_ids
		self.buy_coin = buy_coin
		self.sell_coin = sell_coin
		self.hold_times = hold_times
		self.buy_volume = buy_volume
		self.simulate = simulate
		self.exchange = exchange
		self.exchange_data = exchange_data
		self.log_file = log_file
		self.full_ex = full_ex
		self.base_tickers = set(['BTC','USDT','USDC','DAI','USD','GBP','EUR'])


	# Returns a list of matches from CAPTIAL letter coin symbols of a user specified length 
	def substring_matches(self, text, num_letters, first=False):
		
		# First time check if $COIN is present with $ as the flag
		if first:
			# Special treatment for a special coin
			if 'DOGE' in text:
				return [['DOGE'], self.sell_coin]

			# Look for $ sign
			matches = re.findall('(?<=\$)[^\ ]+', text)
			if matches:
				return [matches, self.sell_coin]

		matches = re.findall('[A-Z]{%d}' % num_letters, text)
		
		# Finding the intersection but maintaining order
		ordered_matches = list(filter(lambda x : x not in self.base_tickers, matches))
		matches = [value for value in ordered_matches if value in self.exchange_data.cryptos]

		# Specific ticker of 1INCH symbol
		new_matches = []
		for i in range(len(matches)):
			if matches[i] == 'INCH':
				matches[i] = '1INCH'
			if matches[i] not in new_matches:
				new_matches.append(matches[i])

		return [new_matches, self.sell_coin]

	# Code to run on tweet
	def on_status(self, status):
	
		# Tweets with mentions
		try:
			# Check tweet is from a user being tracked and that it is not a reply status
			if status.user.id not in self.user_ids or not status.in_reply_to_status_id is None or status.is_quote_status:
				return

			# Handling extended vs not extended tweets
			if not status.truncated:
				full_text = status.text
			else:
				full_text = status.extended_tweet['full_text']

			# Check for retweet
			if full_text.startswith('RT'):
				return

			# Check for substring matches with the keywords speicified for that user and only looking at original non-retweets
			successful = False
			if any(substr in full_text.lower() for substr in self.users[status.user.screen_name]['keywords']):
				if self.full_ex: time.sleep(self.full_ex)

				# Handling a single coin without checking substrings
				if self.buy_coin:

					# Execute buy order
					try:
						pair = [self.buy_coin, self.sell_coin]
						coin_vol = self.exchange_data.buy_sell_vols[self.buy_coin]
						t = threading.Thread(target=self.exchange.execute_trade, args=(pair,), kwargs={'hold_times':self.hold_times, 'buy_volume':coin_vol, 'simulate':self.simulate,'status':status})
						t.start()
						print('\n\n'+'*'*25 + ' Moonshot Inbound! '+'*'*25 + '\n')
						successful=True

					except Exception as e:
						print('\nTried executing trade with ticker %s/%s, did not work' % (self.buy_coin,self.sell_coin))
						print(e)
				
				else:	
					# Loop over possible coin string lengths and get coins, firstflag is the first try to trade, successful is a flag if traded or not
					firstflag = True
					
					# String manipulation and finding coins
					full_text = full_text.replace('\n', ' ')
					full_text = full_text.replace('/',  ' ')
					for i in [3,4,5,2,6]:
						pairs = self.substring_matches(full_text, i, firstflag)
						firstflag = False
						if not pairs[0]:
							continue

						# Loop over the possible buy coins and try to trade
						# Currently will only execute 1 trade which is the first in the trade
						for j in range(len(pairs[0])):
							# Get coin volume from cached trade volumes and execute trade
							try:
								pair = [pairs[0][j], pairs[1]]
								coin_vol = self.exchange_data.buy_sell_vols[pair[0]]

								# Start the buy thread
								t = threading.Thread(target=self.exchange.execute_trade, args=(pair,), kwargs={'hold_times':self.hold_times, 'buy_volume':coin_vol, 'simulate':self.simulate, 'status':status})
								t.start()
								print('\n\n'+'*'*25 + ' Moonshot Inbound! '+'*'*25 + '\n')
								successful = True
								
								# Break means only execute on one coin
								break

							except Exception as e:
								print('\nTried executing trade with ticker %s, did not work' % str(pair))
								# print(traceback.format_exc())
								print(e)
						if successful:
							break

			print('\n\n'+'-'*15 + ' New Tweet ' + '-' * 15)
			print('%s\n@%s - %s:\n\n"%s"' % (datetime.now().strftime('%H:%M:%S'), status.user.screen_name, status.created_at.strftime('%b %d at %H:%M:%S'), full_text))
			
			if not successful:
				print('\nNo valid tickers to trade in tweet')


		except Exception as e:
			print('\nError when handling tweet')
			print(e)

		print('\nRestarting stream\n')

	# Streaming error handling
	def on_error(self, status_code):
		print('Error in streaming: Code %d, sleeping for 10' % status_code)
		if status_code == 420:
			print('Wait for cooloff period to try again\n\nExiting')
			exit()
		time.sleep(10)
		print('\nRestarting stream\n')


# Stream tweets
def stream_tweets(api, users, sell_coin, hold_times, buy_volume, simulate, exchange, keywords=None, log_file=None, buy_coin=None, full_ex=True, exchange_data=None, cancel=[False]):
	
	# Set and list of ids of users tracked
	user_ids_list = [i['id'] for i in users.values()]
	user_ids_set = [int(i) for i in user_ids_list]

	# Get exchange tickers and calculate volumes to buy for each tradeable crypto
	coin_subset = None
	if buy_coin:
		coin_subset = [buy_coin]

	if exchange_data is None:
		exchange_data = exchange_pull(exchange, hold_times, base_coin=sell_coin, coin_subset=coin_subset)
		# Create daemon thread which exits when other thread exits
		daemon = threading.Thread(name='daemon', target=exchange_data.buy_sell_volumes, args=(buy_volume,20*60))
		daemon.setDaemon(True)
		daemon.start()
		time.sleep(3)
	
	# Create the Tweepy streamer
	listener = Listener(users, user_ids_set, sell_coin, hold_times, buy_volume, simulate, exchange, exchange_data, log_file=log_file, buy_coin=buy_coin, full_ex=full_ex)
	stream = Stream(auth=api.auth, listener=listener, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	# Start stream and query prices
	print('\nStarting stream\n')
	

	# Try catch for different termination procedures
	while 1:
		try:
			# Start streaming tweets
			if keywords:
				stream.filter(follow=user_ids_list,track=keywords)
			else:
				stream.filter(follow=user_ids_list)
			
		# Keyboard interrupt kills the whole program
		except KeyboardInterrupt as e:
			stream.disconnect()
			print('\n\n'+'-'*50)
			print('/'*15+'   Stopped Stream   '+'\\'*15)
			print('-'*50)
			print('\nWaiting for trades to finish\n')
			cancel[0] = True
			raise KeyboardInterrupt
		
		# Disconnect the stream and kill the thread looking for prices
		finally:
			print('\nDisconnected Stream\n')
			# exchange_data.stopflag = True
			stream.disconnect()


