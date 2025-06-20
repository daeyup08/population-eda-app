import streamlit as st
import pyrebase
import time
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.firebasestorage.app",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
firestore = firebase.database()
storage = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.user_name = ""
    st.session_state.user_gender = "선택 안함"
    st.session_state.user_phone = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 홈 페이지 클래스
# ---------------------
import streamlit as st

class Home:
    def __init__(self, login_page=None, register_page=None, findpw_page=None):
        st.title("🏠 지역별 인구 분석 EDA 웹앱")

        # 로그인된 경우 사용자 환영 메시지 출력
        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state.get('user_email')}님, 환영합니다!")

        # 프로젝트 소개
        st.markdown("""
        ---
        ### 📊 프로젝트 개요
        이 웹앱은 한국의 지역별 인구 데이터를 바탕으로 다양한 분석 및 시각화를 제공하는 **EDA 플랫폼**입니다.  
        `population_trends.csv` 파일을 업로드하여 각 지역의 인구 변화와 통계 지표를 손쉽게 탐색할 수 있습니다.

        ### 📁 데이터셋 소개
        - **출처**: 통계청 공개 데이터 (예시)
        - **파일명**: `population_trends.csv`
        - **주요 컬럼**:
            - `연도 (year)`
            - `지역 (region)`
            - `인구 (population)`
            - `출생아수(명)`, `사망자수(명)`
        - **특이사항**:
            - 일부 지역(예: '세종')의 결측치는 '-'로 표기되어 있음
            - 연도별 전체/지역별 인구 변화 분석 가능

        ### 🛠️ 기능 안내
        - 연도별 전체 인구 추이 분석
        - 지역별 변화량 및 증감률 계산
        - 누적 영역 시각화, 히트맵 등 시각 분석
        - Streamlit 기반 사용자 인터페이스

        ---
        """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.user_name = user_info.get("name", "")
                    st.session_state.user_gender = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url", "")

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name": name,
                    "gender": gender,
                    "phone": phone,
                    "role": "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email = st.session_state.get("user_email", "")
        new_email = st.text_input("이메일", value=email)
        name = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", "선택 안함"))
        )
        phone = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", ""))

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email = new_email
            st.session_state.user_name = name
            st.session_state.user_gender = gender
            st.session_state.user_phone = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name": name,
                "gender": gender,
                "phone": phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스
# ---------------------
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# 지역 한글 → 영어 변환
def translate_region(name):
    translations = {
        '서울': 'Seoul', '부산': 'Busan', '대구': 'Daegu', '인천': 'Incheon',
        '광주': 'Gwangju', '대전': 'Daejeon', '울산': 'Ulsan', '세종': 'Sejong',
        '경기': 'Gyeonggi', '강원': 'Gangwon', '충북': 'Chungbuk', '충남': 'Chungnam',
        '전북': 'Jeonbuk', '전남': 'Jeonnam', '경북': 'Gyeongbuk', '경남': 'Gyeongnam',
        '제주': 'Jeju', '전국': 'Korea'
    }
    return translations.get(name, name)

class EDA:
    def __init__(self):
        st.title("📊 지역별 인구 분석 EDA")
        uploaded = st.file_uploader("📂 population_trends.csv 업로드", type="csv")
        if not uploaded:
            st.info("CSV 파일을 업로드 해주세요.")
            return

        df = pd.read_csv(uploaded)

        # 전처리
        for col in ['인구', '출생아수(명)', '사망자수(명)']:
            df.loc[df['지역'] == '세종', col] = df.loc[df['지역'] == '세종', col].replace('-', '0')
            df[col] = pd.to_numeric(df[col], errors='coerce')

        tabs = st.tabs(["기초 통계", "연도별 추이", "지역별 분석", "변화량 분석", "시각화"])

        # 1. 기초 통계
        with tabs[0]:
            st.subheader("📌 데이터 구조 (df.info())")
            buffer = io.StringIO()
            df.info(buf=buffer)
            st.text(buffer.getvalue())

            st.subheader("📊 기초 통계량 (df.describe())")
            st.dataframe(df.describe())

            st.subheader("🔎 샘플 데이터")
            st.dataframe(df.head())

        # 2. 연도별 추이
        with tabs[1]:
            st.subheader("📈 전국 인구 추이")
            national = df[df['지역'] == '전국'].sort_values('연도')
            plt.figure(figsize=(10, 5))
            plt.plot(national['연도'], national['인구'], marker='o', label='Population')
            # 예측
            recent = national.tail(3)
            annual_diff = recent['인구'].diff().mean()
            pred_year = 2035
            pred_value = national['인구'].iloc[-1] + annual_diff * (pred_year - national['연도'].iloc[-1])
            plt.axvline(pred_year, linestyle='--', color='gray')
            plt.scatter(pred_year, pred_value, color='red')
            plt.text(pred_year, pred_value, f"{int(pred_value):,}", ha='left')
            plt.title("Total Population Trend")
            plt.xlabel("Year")
            plt.ylabel("Population")
            plt.legend()
            st.pyplot(plt.gcf())

        # 3. 지역별 분석
        with tabs[2]:
            st.subheader("📊 최근 5년간 지역별 인구 변화량")
            recent_years = sorted(df['연도'].unique())[-5:]
            pivot = df[df['연도'].isin(recent_years) & (df['지역'] != '전국')]
            change = pivot.groupby('지역')['인구'].agg(['first', 'last'])
            change['변화량'] = change['last'] - change['first']
            change['증감률'] = (change['변화량'] / change['first']) * 100
            change = change.sort_values('변화량', ascending=False)
            change.index = [translate_region(idx) for idx in change.index]

            fig1, ax1 = plt.subplots()
            sns.barplot(x=change['변화량'] / 1000, y=change.index, ax=ax1)
            ax1.set_title("Population Change (Last 5 Years)")
            ax1.set_xlabel("Change (thousands)")
            for i, v in enumerate(change['변화량'] / 1000):
                ax1.text(v, i, f"{v:.0f}", va='center')
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots()
            sns.barplot(x=change['증감률'], y=change.index, ax=ax2)
            ax2.set_title("Population Growth Rate (%)")
            ax2.set_xlabel("Rate")
            for i, v in enumerate(change['증감률']):
                ax2.text(v, i, f"{v:.1f}%", va='center')
            st.pyplot(fig2)

        # 4. 변화량 분석
        with tabs[3]:
            st.subheader("📉 연도별 인구 증감 상위 100개")
            diff_df = df[df['지역'] != '전국'].sort_values(['지역', '연도'])
            diff_df['증감'] = diff_df.groupby('지역')['인구'].diff()
            top100 = diff_df[['연도', '지역', '증감']].dropna().sort_values('증감', ascending=False).head(100)
            top100['증감'] = top100['증감'].astype(int)
            top100['증감(천명)'] = top100['증감'].apply(lambda x: f"{x:,}")
            def highlight_change(val):
                color = '#d1e5f0' if val > 0 else '#f4cccc'
                return f'background-color: {color}'
            st.dataframe(top100.style.applymap(highlight_change, subset=['증감']))

        # 5. 시각화
        with tabs[4]:
            st.subheader("🌈 누적 영역 그래프 (지역별 인구)")
            pivot_table = df.pivot_table(index='연도', columns='지역', values='인구')
            pivot_table.columns = [translate_region(col) for col in pivot_table.columns]
            pivot_table.fillna(0, inplace=True)
            fig3, ax3 = plt.subplots(figsize=(12, 6))
            pivot_table.plot.area(ax=ax3)
            ax3.set_title("Population by Region Over Time")
            ax3.set_xlabel("Year")
            ax3.set_ylabel("Population")
            st.pyplot(fig3)


# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login    = st.Page(Login,    title="Login",    icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW   = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home     = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User     = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout   = st.Page(Logout,   title="Logout",  icon="🔓", url_path="logout")
Page_EDA      = st.Page(EDA,      title="EDA",     icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()