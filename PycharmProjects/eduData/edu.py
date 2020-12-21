import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pandas as pd

# headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
# 유저 에이전트를 넣어줌으로써 서버에게 브라우저에서 request를 보냈다고 속임.
# res = requests.get(url, headers=headers)
# res.raise_for_status() # 정상적으로 서버에서 HTML 파일을 가져오면 정상적으로 진행. 오류가있으면 이 부분에서 프로그램이 끝남.
# lxml 파서는 서버에서 HTML을 정상적으로 주지 않아서 실패 => 크롬 driver로 파싱하니 성공.
# soup = BeautifulSoup(res.text, 'lxml') # lxml 파서를 통해 bs 객체 만들기



driver = webdriver.Chrome("./chromedriver")

titles = []
paths = []
contents = []
dates = []
nums = []
url = ""


# for => 1 ~ 10 page에 대해서 해줘야함.
for page in range(1,11):
    url = 'https://www1.president.go.kr/petitions/?c=42&only=1&page={}&order=1'.format(page)
    driver.get(url)
    print("curr_url : ", url)
    print("page : ", page)

    time.sleep(3)
    soup = bs(driver.page_source, 'html.parser') # 3초가 끝나면 새로운 page의 url로 접속하고 파서가 파싱한다.

    # 현 page에서 petition 요소에 접근
    lists = soup.find("div", attrs={"class": "ct_list1"})
    ul = lists.find("ul", attrs={"class": "petition_list"})
    a_lists = ul.find_all("a", attrs={"class": "cb relpy_w"})  # 현재 페이지의 "전체목록" 내부에 있는 모든 a 태그들을 리스트로 반환.

    # path를 추가하기 전에 현재 paths 리스트에 몇개가 들어있는지 확인한다 => 2 page가 되면 paths 리스트의 7번 index부터 읽어야하기 때문
    path_len = len(paths)
    print(a_lists)
    for a in a_lists: # 현재 page 내에서 각 petition의 title과 path를 파싱하여 paths, titles 배열에 저장.
        # print(a.attrs["href"]) path 배열에 들어갈 경로 "/petition/12345"
        paths.append(a.attrs["href"])  # 각 청원의 path를 저장.
        # print(a.text[3:].strip()) titles
        titles.append(a.text[3:].strip())  # 각 청원의 title을 titles 배열에 저장.

    new_paths = paths[path_len:] # page 별로 해당하는 path만 읽어야하므로 => 2 page가 되면 paths 리스트의 7번 index부터 읽어야하기 때문
    print("new_paths : ", new_paths)
    for path in new_paths: # 현재 page의 모든 petition들의 해당 url에 접속하여 content를 파싱.
        url = "https://www1.president.go.kr" + path
        driver.get(url)
        soup = bs(driver.page_source, 'html.parser') # 각 url에 대하여 soup 객체를 새로 생성한다.

        # contents 추가하기.
        content = soup.find("div", attrs={"class":"View_write"})
        data = content.text.strip()
        data = data.replace("\n", "") # \n 문자도 제거
        print(data)

        # date 추가하기.
        date_ul = soup.find("ul", attrs={"class": "petitionsView_info_list"})
        li = date_ul.li.next_sibling.next_sibling
        li_data = li.text[4:]
        print(li.text[4:])

        # num 추가하기.
        h2 = soup.find("h2", attrs={"class": "petitionsView_count"})
        num = h2.find('span', attrs={"class": "counter"})
        num = num.text
        print(num)

        contents.append(data) # 공백 제거한 data를 리스트에 저장.
        dates.append(li_data)
        nums.append(num)
driver.close()


# 최종 값
print("titles : ", titles)
print("paths : ", paths)
print("contents : ", contents)
print("dates : ", dates)
print("nums : ", nums)


my_dictionary = {"title": titles, "date": dates, "num": nums, "contents": contents}
data = pd.DataFrame(my_dictionary)  # 전체 데이터를 긁은 list인 total을 dataframe으로 변환시켜주면서 각 column의 이름을 부여해줍니다.
print(data)

datatitle = input("Please set the title of this excel file : ")  # 긁어온 데이터를 저장할 xlsx 파일의 이름을 지정해줍니다.
data.to_excel(datatitle + ".xlsx")



# ----------------- 참고 자료 ---------------- #
# soup.a
# soup.a.attrs
# soup.a["href"]
# soup.find("a", href={"class":"Nbtn_upload"})
# soup.find(href={"class":"Nbtn_upload"})
#
# soup.find_all("a", attrs={"class":"cb relpy_w"})
#
# rank1 = soup.find('li', attrs={"class":"rank01"})
# rank1.next_sibling.next_sibling
# rank2 = rank1.find_next_sibling("li")
#
# print(soup.find("a", attrs={"class":"Nbtn_upload"}))
#
# cartoons = soup.find_all('div', attrs={'class':'rating_type'})
# for cartoon in cartoons:
#     rate = cartoon.find('strong').get_text()
