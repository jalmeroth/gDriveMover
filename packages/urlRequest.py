#!/usr/bin/python
import requests
import threading
import Queue


class URLRequestThread(threading.Thread):
	"""docstring for URLRequestThread"""
	def __init__(self, queue, method, url, **kwargs):
		super(URLRequestThread, self).__init__()
		self.method = method
		self.url = url
		self.queue = queue
		self.kwargs = kwargs
		
	def run(self):
		"""docstring for run"""
		r = requests.request(self.method, self.url, **self.kwargs)
		self.queue.put((self.getName(),r))

def main():
	"""docstring for main"""
	urls = [
		"http://www.almeroth.com",
		"http://blog.almeroth.com",
		"http://freizeit.almeroth.com",
		"http://www.intosystems.de",
		"http://www.intosite.de"
	]
	
	headers = {
		"Content-Type": "application/json",
	}

	threads = []
	q = Queue.Queue()

	for i in range(len(urls)):
		new_thread = URLRequestThread(
			q,
			"GET",
			urls[i],
			headers=headers
		)
		new_thread.setName(i)
		threads.append(new_thread)
		new_thread.start()

	for t in threads:
		t.join()

	output = {}
	while not q.empty():
		url, data = q.get()
		output[url] = data.status_code

	print output

if __name__ == '__main__':
	main()