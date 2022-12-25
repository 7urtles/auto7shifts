from flask import Flask, request
from bots.DataScraper import DataCollector
from tools.shifts import ShiftPool, Shift
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook_test():
	trigger()
	return 'success'



def trigger():
	scraper = DataCollector('charleshparmley@icloud.com', 'Earthday19!@22')
	scraper.run()
	pool = ShiftPool(scraper.shift_pool)
	[print(pool.shifts[shift]) for shift in pool.shifts]
	return 'success'


app.run(host="0.0.0.0", port=5007, debug=True)


