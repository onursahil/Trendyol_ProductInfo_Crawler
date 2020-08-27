from bs4 import BeautifulSoup
import requests
import csv
import re
import time

agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

def write_to_file(product):
    print("\nWRITING TO FILE...")
    header = ['link', 'category', 'title', 'information', 'original_price', 'discount_price']
    with open('trendyol_loreal.csv', mode='w', encoding='utf-8', newline='') as data_csv:
        dict_writer = csv.DictWriter(data_csv, fieldnames=header, dialect='excel')
        dict_writer.writeheader()
        dict_writer.writerows(product)


def crawl(START_PAGE, pi):
    print("\nSTARTED CRAWLING DATA...")
    products = []
    for i in range(1, pi+1):
        START_PAGE = START_PAGE + '&pi' + str(i)
        r = requests.get(START_PAGE, headers=agent)
        soup = BeautifulSoup(r.content, "lxml")
        product_div = soup.findAll('div', attrs={"class": "p-card-chldrn-cntnr"})
        for i in range(len(product_div)):
            product = {}
            # print("{}th product".format(i + 1))
            link = product_div[i].find('a', href=True)['href']

            # PRODUCT LINK
            product_link  = 'https://www.trendyol.com/' + link

            product_page = requests.get(product_link, headers=agent)
            product_soup = BeautifulSoup(product_page.content, "lxml")

            # PRODUCT IMAGE
            product_img = []
            try:
                img_div = product_soup.findAll("div", attrs={"class": "pd-img"})
                for el in img_div:
                    img = el.find("img")
                    product_img.append(img['src'])
            except:
                print("Image Not Found!")
                continue
            
            # PRODUCT CATEGORY
            product_path = product_soup.findAll("a", attrs={"class": "breadcrumb-item"})
            try:
                product_category = product_path[len(product_path) - 2].get_text()
            except:
                product_category = ""
                continue

            # PRODUCT TITLE
            product_title = product_soup.find('span', attrs={"class": "pr-nm"}).get_text()

            # PRODUCT INFORMATION
            product_info = product_soup.find("div", attrs={"class": "pr-in-dt-cn"}).get_text()
            
            def correction(s):
                res = re.sub('\s+$', '', re.sub('\s+', ' ', re.sub('\.', '. ', s)))
                if res[-1] != '.':
                    res += '.'
                return res
            info = correction(product_info)
            pos_beg = info.find('belirlemektedir')
            info = info[pos_beg+17:]

            info = re.sub('([.,!?()])', r'\1 ', info)
            info = re.sub('\s{2,}', ' ', info)

            info_word_list = info.split()

            for i in range(2):
                for i in range(len(info_word_list)):
                    word = info_word_list[i]
                    pattern = re.compile("[A-Z]")
                    start = 0
                    while True:
                        m = pattern.search(word, start + 1)
                        if m == None:
                            break
                        start = m.start()
                        
                        word = word[:start] + " " + word[start:]
                        break
                    info_word_list[i] = word
            
            new_info = " ".join(info_word_list)
            new_info = re.sub(r'\s+', ' ', new_info)

            # PRODUCT SCORE
            # score_part = product_soup.findAll("div", attrs={"class": "pr-rnr-cn gnr-cnt-br"})

            # PRODUCT ORIGINAL - DISCOUNT PRICE
            product_org_price = product_soup.find('span', attrs={"class": "prc-org"}).get_text()
            product_discount_price = product_soup.find('span', attrs={"class": "prc-slg"}).get_text()


            product['link'] = product_link
            product['category'] = product_category
            product['title'] = product_title
            product['information'] = new_info
            product['original_price'] = product_org_price
            product['discount_price'] = product_discount_price

            print(product)
            # time.sleep(3)
            products.append(product)
            print(len(products))
    print("\nCRAWLING ENDED...")
    return products


def infinite_rolling(START_PAGE):
    print("FINDING NUMBER OF SECTIONS...")
    r = requests.get(START_PAGE, headers=agent)
    soup = BeautifulSoup(r.content, "lxml")

    page_result = soup.find('div', attrs={"class": "dscrptn"})
    page_result = page_result.get_text()
    pos1 = page_result.find("için")
    pos2 = page_result.find("sonuç")
    product_num = int(page_result[pos1+5: pos2-1])

    if product_num % 24 == 0:
        pi = product_num // 24
    else:
        pi = (product_num // 24) + 1

    return pi

def main():
    START_PAGE = "https://www.trendyol.com/tum--urunler?satici=107819"
    pi = infinite_rolling(START_PAGE)
    product = crawl(START_PAGE, pi)
    write_to_file(product)

if __name__ == "__main__":
    main()