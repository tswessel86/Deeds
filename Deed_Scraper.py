from pyautogui import screenshot
from pytesseract import Output, image_to_string
from datetime import date, datetime, timedelta
from time import sleep
from pandas import DataFrame

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://records.larimer.org/LandmarkWeb/Account/LogOn"
HOME_URL = "https://records.larimer.org/LandmarkWeb"

# SEARCH INPUTS
DOC_TYPE = 'DT'
NUM_RECORDS = 'Show first 2000 records'
NUM_TO_DISPLAY = 'All'

XPATHS = {
	'username' : '//*[@id="UserName"]',
	'pwd' : '//*[@id="Password"]',
	'logon_btn' : '//*[@id="bodySection"]/div/div/form/div/fieldset/p/input',
	'logout_btn' : '//*[@id="idLogonName"]',

	'doc_search' : '//*[@id="bodySection"]/div/div/div[3]/div/div[2]/a/img',
	'accept_disclaimer' : '//*[@id="idAcceptYes"]',
	'search_section' : '//*[@id="searchCriteriaDocuments"]',
	'doc_type' : '//*[@id="documentType-DocumentType"]',
	'begin_date' : '//*[@id="beginDate-DocumentType"]',
	'end_date' : '//*[@id="endDate-DocumentType"]',
	'num_records' : '//*[@id="numberOfRecords-DocumentType"]',
	'search_btn' : '//*[@id="submit-DocumentType"]',
	'num_to_display' : '//*[@id="displaySelect"]/select',

	'num_returned' : '//*[@id="resultsTable_info"]/b',
	'all_results' : '//*[@id="resultsTable"]/tbody',

	'back_to_results_btn' : '//*[@id="returnToSearchButton"]',
	'zoom_out' : '//*[@id="zoomOut"]',

	'instrument_num' : '//*[@id="documentInformationParent"]/table/tbody/tr[1]/td[2]',
	'record_date' : '//*[@id="documentInformationParent"]/table/tbody/tr[3]/td[2]',
	'grantor' : '//*[@id="documentInformationParent"]/table/tbody/tr[8]/td[2]',
	'grantee' : '//*[@id="documentInformationParent"]/table/tbody/tr[9]/td[2]',
	'doc_link' : '//*[@id="documentInformationParent"]/table/tbody/tr[10]/td[2]',
	'pdf' : '//*[@id="documentImageInner"]', # use src of this element

}

FHA_VA_DEEDS = []
IMG_PATH = 'deed.png'
SEARCH_TERMS = ['veterans affairs', 'fha']
DAYS_PER_SEARCH = timedelta(days=15)


def read_login():
	with open('login.txt', 'r') as f:
		login_raw =_raw = f.readlines()
	f.close()
	user = "".join(login_raw[0].split(':')[1].split())
	pwd = "".join(login_raw[1].split(':')[1].split())
	return [user, pwd]


def login(driver, creds):
	driver.get(LOGIN_URL)
	username_input = WebDriverWait(driver, 15).until(
		EC.element_to_be_clickable((By.XPATH, XPATHS.get('username')))
	)
	username_input.send_keys(creds[0])

	pwd_input = WebDriverWait(driver, 15).until(
		EC.element_to_be_clickable((By.XPATH, XPATHS.get('pwd')))
	)
	pwd_input.send_keys(creds[1])

	logon_btn = WebDriverWait(driver, 15).until(
		EC.element_to_be_clickable((By.XPATH, XPATHS.get('logon_btn')))
	)
	logon_btn.click()
	return


def logout(driver):
	driver.get(HOME_URL)
	logout_btn = WebDriverWait(driver, 15).until(
		EC.element_to_be_clickable((By.XPATH, XPATHS.get('logout_btn')))
	)
	logout_btn.click()
	return


def get_search_dates():
	b_date_str = str(input('Begin Date (mm/dd/yyyy): '))
	b_date_tuple = b_date_str.split("/")
	b_date = date(year=int(b_date_tuple[2]), month=int(b_date_tuple[0]), day=int(b_date_tuple[1]))
	e_date_str = str(input('End Date (mm/dd/yyyy): '))
	e_date_tuple = e_date_str.split("/")
	e_date = date(year=int(e_date_tuple[2]), month=int(e_date_tuple[0]), day=int(e_date_tuple[1]))
	search_dates = get_all_search_periods(b_date, e_date)
	return search_dates


def get_all_search_periods(beg, end):
	search_dates = []
	curr = beg

	while curr < end:
		curr = beg + DAYS_PER_SEARCH
		if curr > end:
			curr = end
		search_dates.append([datetime.strftime(beg, "%m/%d/%Y"), datetime.strftime(curr, "%m/%d/%Y")])
		beg = curr+timedelta(days=1)

	return search_dates


def get_num_results(driver, beg, end):
	try:
		results = WebDriverWait(driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('num_returned')))
		)
		total_res = results.text.split(' of ')[1]
		if int(total_res) > 2000:
			print("Over 2000 results returned for date range: " + beg + " to " + end)
		return total_res
	except:
		return "Unable to get number of results"


def search_docs(doc_driver, search_periods):

	for x in search_periods:
		start_date = x[0]
		end_date = x[1]
		
		search_options = Options()
		search_options.headless = True
		search_driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=search_options)
		search_driver.get(HOME_URL)
		
		doc_btn = WebDriverWait(search_driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('doc_search')))
		)
		doc_btn.click()

		accept_btn = WebDriverWait(search_driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('accept_disclaimer')))
		)
		accept_btn.click()

		try:
			doc_type_input = WebDriverWait(search_driver, 15).until(
				EC.element_to_be_clickable((By.XPATH, XPATHS.get('doc_type')))
			)
			doc_type_input.clear()
			doc_type_input.send_keys(DOC_TYPE)

			begin_date_input = WebDriverWait(search_driver, 15).until(
				EC.element_to_be_clickable((By.XPATH, XPATHS.get('begin_date')))
			)
			begin_date_input.clear()
			begin_date_input.send_keys(start_date)

			end_date_input = WebDriverWait(search_driver, 15).until(
				EC.element_to_be_clickable((By.XPATH, XPATHS.get('end_date')))
			)
			end_date_input.clear()
			end_date_input.send_keys(end_date)

			num_records_input = WebDriverWait(search_driver, 15).until(
				EC.element_to_be_clickable((By.XPATH, XPATHS.get('num_records')))
			)
			num_records_input.send_keys(NUM_RECORDS) 

			search_btn = WebDriverWait(search_driver, 15).until(
				EC.element_to_be_clickable((By.XPATH, XPATHS.get('search_btn')))
			)
			search_btn.click()

			num_to_display = WebDriverWait(search_driver, 15).until(
				EC.element_to_be_clickable((By.XPATH, XPATHS.get('num_to_display')))

			)
			num_to_display.send_keys(NUM_TO_DISPLAY)

			total_res = get_num_results(search_driver, start_date, end_date)
			print(total_res + " results found for date range " + start_date + " thru " + end_date)

			get_all_results(search_driver, doc_driver)

			print("Completed search from " + start_date + " to " + end_date)

		except TimeoutException:
			print("Timeout. Skipped date range: " + start_date + " through " + end_date)

		search_driver.quit()

	# df = pd.DataFrame(FHA_VA_DEEDS, columns=['Grantor', 'Grantee', 'Deed Type', 'Record Date', 'Instrument #'])	
	df = DataFrame(FHA_VA_DEEDS, columns=['Grantor', 'Grantee', 'Deed Type', 'Record Date', 'Instrument #'])	
		
	filename = "Deeds_" + search_periods[0][0].replace("/", "-") + "_thru_" + search_periods[-1][1].replace("/","-") + ".xlsx"
	df.to_excel(excel_writer=filename, index = False)
	print("Search complete. Data recorded.")

	return


def get_results_table(search_driver):
	try: 
		results_table = WebDriverWait(search_driver, 20).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('all_results')))
		)
		return results_table
	except TimeoutException:
		print ("No results for this search.")
		return


def get_all_results(search_driver, doc_driver):
	results_table = get_results_table(search_driver)
	count = 0

	while count < len(results_table.find_elements_by_xpath('./tr/td[1]')):
		row = results_table.find_elements_by_xpath('./tr/td[1]')[count]
		print(str(count+1))
		record = get_record(row, search_driver, doc_driver)
		count += 1
		if record != 0:
			entry = [
				record.get('grantor'),
				record.get('grantee'),
				record.get('deed_type'),
				record.get('record_date'),
				record.get('instrument_num')
			]
			FHA_VA_DEEDS.append(entry)
		go_back(search_driver)
		results_table = get_results_table(search_driver)

	return


def get_record(row, search_driver, doc_driver):
	row.click()
	unreleased = check_for_doc_link(search_driver)
	record = 0
	if unreleased:
		if (load_pdf(search_driver, doc_driver) == 1):
			deed_type = search_text()
			if deed_type in SEARCH_TERMS:
				record = get_data(search_driver, deed_type)
	return record


def load_pdf(search_driver, doc_driver):
	try:
		pdf_src = WebDriverWait(search_driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('pdf')))
		)
		doc_driver.get(pdf_src.get_attribute('src'))
		# time.sleep(0.4)
		sleep(0.4)
		take_screenshot()
		return 1
	except TimeoutException:
		print("Couldn't load pdf.")
		return -1


def check_for_doc_link(driver):
	try:
		doc_link = WebDriverWait(driver, 5).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('doc_link')))
		)
		if "release of deed of trust" in doc_link.text.lower():
			return 0
		else:
			return 1
	except TimeoutException:
		print("Timed out searching for doc link.")
		return 1
	except NoSuchElementException:
		print("Doc link doesn't exist.")
		return 1


def take_screenshot():
	# scrn = pyautogui.screenshot()
	scrn = screenshot()
	scrn.save(IMG_PATH)
	return


def search_text():
	# txt = pytesseract.image_to_string(IMG_PATH).lower()
	txt = image_to_string(IMG_PATH).lower()
	for t in SEARCH_TERMS:
		if t in txt:
			print("Found: " + t)
			return t
	return


def get_data(driver, deed_type):
	try:
		instrument_num = WebDriverWait(driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('instrument_num')))
		)

		record_date = WebDriverWait(driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('record_date')))
		)

		grantor = WebDriverWait(driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('grantor')))
		)

		grantee = WebDriverWait(driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('grantee')))
		)

		return {
			'deed_type' : deed_type, #C
			'instrument_num' : instrument_num.text, #E
			'record_date' : record_date.text, #D
			'grantor' : grantor.text.replace("\n", ", "), #A
			'grantee' : grantee.text.replace("\n", ", "), #B
		} 

	except:
		print("Couldn't get data.")
		return


def go_back(search_driver):
	try:
		back_to_results_btn = WebDriverWait(search_driver, 15).until(
			EC.element_to_be_clickable((By.XPATH, XPATHS.get('back_to_results_btn')))
		)
		back_to_results_btn.click()
	except TimeoutException:
		print("Timed out looking for back button.")
	except NoSuchElementException:
		print("No back button present.")


if __name__ == "__main__":
	dates = get_search_dates()
	ogStartTime = datetime.now()
	print("Program starting at time: " + str(ogStartTime))
	doc_options = Options()
	doc_options.add_argument('--start-maximized')
	doc_driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=doc_options)
	
	creds = read_login()
	login(doc_driver, creds)
	search_docs(doc_driver, dates)
	logout(doc_driver)
	doc_driver.quit()
	print("Program completed with elapsed time: ")
	print(datetime.now() - ogStartTime)
	input("Press Enter to exit program...")
