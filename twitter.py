import multiprocessing as mp
import pandas as pd
import threading
import datetime
import calendar
import asyncio
import getopt
import queue
import twint
import math
import sys
import os
import re

OUTPUT_FLDR_PRFX = 'tweets'
OUTPUT_FILE_NAME = 'tweets'

# https://stackoverflow.com/questions/24251219/pandas-read-csv-low-memory-and-dtype-options
# https://stackoverflow.com/questions/17557074/memory-error-when-using-pandas-read-csv
DTYPES = {
	'cashtags' : object,
	'conversation_id' : str,
	'created_at' : str,
	'date' : str,
	'geo' : object,
	'hashtags' : object,
	'id' : str,
	'language' : str,
	'likes_count' : str,
	'link' : str,
	'mentions' : object,
	'name' :str,
	'near' : object,
	'photos' : object,
	'place' : object,
	'quote_url' : str,
	'replies_count' : str,
	'reply_to' : object,
	'retweet' : object,
	'retweet_date' : str,
	'retweet_id' : str,
	'retweets_count' : int,
	'source' : object,
	'thumbnail' : str,
	'time' : str,
	'timezone' : str,
	'trans_dest' : object,
	'trans_src' : object,
	'translate' : object,
	'tweet' : str,
	'urls' : object,
	'user_id' : str,
	'user_rt' : object,
	'user_rt_id' : str,
	'username' : str,
	'video' : str
}

def daterange(start, final):
	yield from [start + datetime.timedelta(days=d) for d in range(0, int((final - start).days))]

def extract_year(date_str):
	return date_str[:date_str.find('-')]

def extract_month(date_str):
	return date_str[date_str.find('-')+1 : date_str.rfind('-')]

def get_path(date_str, suffix=''):
	return os.path.join(
		OUTPUT_FLDR_PRFX + extract_year(date_str), extract_month(date_str), 
		date_str + '-{}.csv'.format(OUTPUT_FILE_NAME + suffix.replace(' ', '-'))
	)

def get_config(query, since, until):
	config = twint.Config()
	config.Search = '%24' + query
	config.Lang = 'en'
	config.Since = since
	config.Until = until
	config.Hide_output = True
	config.Store_csv = True
	config.Output = get_path(since, suffix='-'+config.Search)

	# For some reason, twint changes Since and Until under the
	# hood, so, we'll put the real values in our own variables
	config.since = since
	config.until = until

	return config

def get_inputs(start, end, query, processes, threads):
	# NOTE: To get all tweets on say 2018-01-01, you need to specify that:
	# since = 2018-01-01 AND until = 2018-01-04 (i.e. you need 3 extra days to avoid data loss)
	chunk = math.ceil((end - start).days / processes)
	confs = []
	for d in daterange(start, end):
		since = d.strftime('%Y-%m-%d')
		until = (d + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
		confs.append(get_config(query, since, until))	
	return [(confs[i:chunk+i], threads) for i in range(0, len(confs), chunk)]

def process_chunk(chunk, since, o_path, **to_csv_kwargs):
	copy = chunk.copy()
	copy['date'] = pd.to_datetime(copy['date'] + ' ' + copy['time'])
	copy = copy[(copy['date'] >= since.replace(hour=00, minute=00, second=00)) &\
				(copy['date'] <= since.replace(hour=23, minute=59, second=59))]
	copy.drop(columns='time', inplace=True)
	copy.to_csv(o_path, **to_csv_kwargs)

def task(q, stop_event):
	asyncio.set_event_loop(asyncio.new_event_loop())
	while not stop_event.is_set():
		try:
			config = q.get(timeout=0.5)
			i_path = get_path(config.since, suffix='-'+config.Search)
			o_path = get_path(config.since, suffix='-{}-compressed'.format(config.Search))
			if not os.path.exists(o_path):
				twint.run.Search(config)
				since = datetime.datetime.strptime(config.since, '%Y-%m-%d')
				readr = pd.read_csv(i_path, dtype=DTYPES, chunksize=1000)
				process_chunk(next(readr), since, o_path
					, index=False
					, header=True
					, mode='w'
					, compression='gzip'
				)
				for chunk in readr:
					process_chunk(chunk, since, o_path
						, index=False
						, header=False
						, mode='a'
						, compression='gzip'
					)
				os.remove(i_path)
		except queue.Empty:
			continue
		q.task_done()

def scrape(configs, max_threads):
	thread_lst = []
	stop_event = threading.Event()
	outpt_lock = threading.Lock()
	work_queue = queue.Queue()

	for c in configs:
	    work_queue.put(c)

	for i in range(max_threads):
	    thread_lst.append(
	    	threading.Thread(
	    		target=task, 
	    		args=(work_queue, stop_event)
    		)
    	)
	    thread_lst[i].start()

	work_queue.join()
	stop_event.set()
	for t in thread_lst: t.join()

def parse(argv):
	opts, args = getopt.getopt(argv, "s:e:q:p:t:")
	s, e, q, p, t = None, None, None, None, None
	for opt, arg in opts:
		if opt in ['-s']: s = str(arg)
		if opt in ['-e']: e = str(arg)
		if opt in ['-q']: q = str(arg)
		if opt in ['-p']: p = int(arg)
		if opt in ['-t']: t = int(arg)
	if q is None: 	q = 'bitcoin'
	if s is None:	raise ValueError('Start date is required.')
	if e is None: 	raise ValueError('End date is required.')
	s = datetime.datetime.strptime(s, '%Y-%m-%d')
	e = datetime.datetime.strptime(e, '%Y-%m-%d')
	if s >= e:	 	raise ValueError('Start date must come before end date.')
	return s, e, q, p, t

def create_folders(start, end):
	for d in daterange(start, end):
		year = OUTPUT_FLDR_PRFX + str(d.year)
		mnth = extract_month(d.strftime('%Y-%m-%d'))
		path = os.path.join(year, mnth)
		if not os.path.exists(year):
			os.mkdir(year)
			os.mkdir(path)
		else:
			if not os.path.exists(path): os.mkdir(path)
	
def take_input_if(cond, msg=''):
	if cond:
		are_you_sure = ''
		msg += " Would you like to continue?\n(y/n): "
		while not re.match(r'^[y|n]$', are_you_sure.lower()):
			are_you_sure = input(msg)
		if are_you_sure == 'n':
			print('Exiting...')
			sys.exit()

if __name__== '__main__':

	print('Script started!')

	try:
		start, final, query, proc, thrd = parse(sys.argv[1:])
	except (getopt.GetoptError, ValueError) as e:
		print(e)
		sys.exit()

	take_input_if(proc is None and thrd is None, "You are about to use all processing power available.")
	ndays = (final - start).days
	if proc  is None: proc = mp.cpu_count()
	if thrd  is None: thrd = math.ceil(ndays / proc)
	take_input_if(ndays > proc * thrd, 
		"Number of workers ({}) is less than the number of jobs ({}). This may take a while.".format(proc * thrd, ndays)
	)

	try:
		print('Creating directories...\t', end='')
		create_folders(start, final)
		print('done!')
	except Exception as e:
		print(e)
		sys.exit()

	inputs = get_inputs(start, final, query, proc, thrd)

	start = datetime.datetime.now()
	print('Start time: ', start.strftime('%Y-%m-%d %H:%M:%S'))
	print('Processing...')
	sys.stdout.flush()

	with mp.Pool(processes=proc) as pool:
		results = pool.starmap(scrape, inputs)
	
	final = datetime.datetime.now()
	print('Final time: ', final.strftime('%Y-%m-%d %H:%M:%S'))
	print('Total time: ', final - start)
	sys.stdout.flush()
