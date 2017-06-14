import os
import urllib
import urllib2
import lxml.html
import multiprocessing
import selenium_lib

search_xpath = "//div[@class='result_search']/dl/dt"
search_title_xpath = "./a[@class='manga_info name_one']"
search_last_chapter_xpath = "./a[@class='name_two']"
chapters_xpath = "//div[@class='manga_detail']/div[@class='detail_list']/ul[1]/li"
chapter_detail_xpath = "./span/a"
image_xpath = "//section[@class='read_img']/a/img[@id='image']"
next_image_xpath = "//section[@class='read_img']/a"


def get_xpath_doc(url):
	response = urllib2.urlopen(url).read()
	return lxml.html.fromstring(response)


def get_xpath_doc_image(driver, url):
	driver.get(url)
	selenium_lib.wait_for_element(driver, image_xpath)
	return lxml.html.fromstring(driver.page_source)


def safe_to_string(string):
	return string.encode('utf-8').strip()


def get_comic():
	query = raw_input('input search query : ')
	comics = search(query)
	print("------------------ Found Results ---------------")
	for i, comic in enumerate(comics, start=1):
		print('{}. {} --Last Update : {}--'.format(i, comic.get('title'), comic.get('last_chapter')))

	index = -1
	comic = None
	while index < 0:
		index = int(raw_input('Pick comic number : ')) - 1
		if index < 0 or index >= len(comics):
			index = -1
			continue
		else:
			comic = comics[index]
			comic['chapters'] = get_chapters(comic)
	return comic


def search(query):
	url = 'http://www.mangahere.co/search.php?name={}'.format(query)
	html = get_xpath_doc(url)
	comics = []
	for el in html.xpath(search_xpath):
		title = el.xpath(search_title_xpath)[0]
		chapter = el.xpath(search_last_chapter_xpath)[0]
		comic = {
			'title': safe_to_string(u'{}'.format(title.xpath('./text()')[0])),
			'title_url': title.xpath('./@href')[0],
			'last_chapter': chapter.xpath('./text()')[0]
		}
		comics.append(comic)
	return comics


def get_chapters(comic):
	html = get_xpath_doc(comic.get('title_url'))
	chapters = []
	for el in html.xpath(chapters_xpath):
		link = el.xpath(chapter_detail_xpath)[0]
		chapter = {
			'name': str(link.xpath('./text()')[0]).strip(),
			'url': link.xpath('./@href')[0]
		}
		chapters.append(chapter)
	return chapters


def downloads(comic):
	print('Downloading {} chapters of {}...'.format(len(comic.get('chapters')), comic.get('title')))
	for ch in comic.get('chapters'):
		dir = '{}/{}'.format(comic.get('title'), ch.get('name'))
		if not os.path.exists(dir):
			os.makedirs(dir)
		ch['dir'] = dir
	pool = multiprocessing.Pool(multiprocessing.cpu_count())
	pool.map(download_chapter, comic.get('chapters'))
	pool.close()
	pool.join()


def download_chapter(chapter):
	print('Downloading chapter {}...'.format(chapter.get('name')))
	driver = selenium_lib.get_chrome_instance(10)
	download_images(driver, chapter.get('url'), chapter.get('dir'), 1)
	selenium_lib.quit_driver(driver)
	print('Finished downloading chapter {}'.format(chapter.get('name')))


def download_images(driver, url, dir, seq):
	driver.get(url)
	image = driver.find_element_by_xpath(image_xpath).get_attribute('src')
	image_dir = '{}/{}.jpg'.format(dir, seq)
	urllib.urlretrieve(image, image_dir)

	next_image = driver.find_element_by_xpath(next_image_xpath).get_attribute('href')
	if next_image.startswith('http'):
		print('Downloaded {}.'.format(image_dir))
		download_images(driver, next_image, dir, seq + 1)


def main():
	comic = get_comic()
	print("\n------------------ Chapters ---------------")
	for i, ch in enumerate(comic.get('chapters'), start=1):
		print('{}. {}'.format(i, ch.get('name')))
	print('\n')

	start_chapter = raw_input('Select start chapter : ')
	end_chapter = raw_input('Select end chapter : ')
	start_chapter = 0 if start_chapter == '' else int(start_chapter) - 1
	end_chapter = len(comic.get('chapters')) if end_chapter == '' else int(end_chapter)

	comic['chapters'] = comic.get('chapters')[start_chapter:end_chapter]
	downloads(comic)


if __name__ == "__main__":
	main()
