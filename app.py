import streamlit as st
import pandas as pd

import requests
from bs4 import BeautifulSoup
from urllib import parse
import time

import smtplib
from email.mime.text import MIMEText

st.set_page_config(
    page_title="전북대학교 공지사항 구독",
    page_icon="",
    layout="wide"
)

col1, col2 = st.columns(2)
with col1:
    st.image("Image/logo_tr.png")

    st.subheader("공지사항 구독서비스 이용 방법")
    st.caption("6시간마다 정보를 받아오기때문에 바로 공지를 확인할 수는 없습니다.")

    st.text("1. 공지사항 메뉴 선택")
    st.image("Image/menu.png")
    st.text("2. 알림 받고 싶은 제목에 들어가는 키워드(한단어)입력")
    st.caption("ex) 벨트 취득 => Belt")
    st.text("3. 이메일 주소 입력하기")
    st.text("4. 구독버튼 누르기")

with col2:
    tab1, tab2 = st.tabs(["구독", "구독취소"])
    with tab1:
        menu = st.radio(label="메뉴 선택", options=["교육", "국제", "등록", "병무", "입학", "장학", "총무", "취업", "학사", "행사", "기타"])
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

        keyword = st.text_input("키워드", value="", key="keyword")
        email = st.text_input("이메일 주소", key="email")

        if st.button("구독"):
            if not keyword:
                st.error("키워드를 입력하세요!")
            else:
                df = pd.DataFrame({"keyword": [keyword], "email": [email]})
                df.to_csv("emails.csv", mode="a", index=False)
                st.success("구독이 완료되었습니다!")

                url = f"https://www.jbnu.ac.kr/kor/?menuID=139&category={parse.quote(menu)}"
                last_title = ""

                sender_email = "보내는사람 메일 주소 입력"
                sender_pw = "보내는사람 메일 비밀번호 입력"
                receiver_email = email

                while True:
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text, "html.parser")
                    lists = soup.find_all("a")

                    for item in lists:
                        item = f"'{item}'"
                        soup_t = BeautifulSoup(item, "html.parser")
                        title = soup_t.a.get("title")
                        href = soup_t.a.get("href")

                        if (title is not None) and (keyword.lower() in title.lower() and title != last_title):
                            link = f"https://www.jbnu.ac.kr/kor/{href}"
                            last_title = title

                            msg = MIMEText(f"{title} \n \n {link}")
                            msg["Subject"] = f"[공지 알림] {keyword}관련 새로운 공지"
                            msg["From"] = sender_email
                            msg["To"] = receiver_email

                            smtp = smtplib.SMTP('smtp.gmail.com', 587)
                            smtp.starttls()
                            smtp.login(sender_email, sender_pw)

                            smtp.sendmail(sender_email, receiver_email, msg.as_string())
                            smtp.quit()

                    time.sleep(21600)

    with tab2:
        st.text("* 구독 서비스가 취소됩니다.")
        email = st.text_input("이메일 주소", key="del_email")
        df = pd.read_csv("emails.csv")
        if st.button("구독취소"):
            if email not in df["email"].values:
                st.write("다시 입력해주세요.")
            else:
                df = df[df["email"] != email]
                df.to_csv("emails.csv", index=False)
                st.success("구독이 취소되었습니다.")