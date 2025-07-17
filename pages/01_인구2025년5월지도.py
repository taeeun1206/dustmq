import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("2025년 5월 기준 행정구역별 인구 지도 (핑크 원 시각화)")

# 중심 좌표 (행정구역명 → 위도/경도) 일부 예시
region_coords = {
    '서울특별시': (37.5665, 126.9780),
    '부산광역시': (35.1796, 129.0756),
    '대구광역시': (35.8722, 128.6025),
    '인천광역시': (37.4563, 126.7052),
    '광주광역시': (35.1595, 126.8526),
    '대전광역시': (36.3504, 127.3845),
    '울산광역시': (35.5384, 129.3114),
    '세종특별자치시': (36.4801, 127.2890),
    '경기도': (37.4138, 127.5183),
    '강원특별자치도': (37.8228, 128.1555),
    '충청북도': (36.6357, 127.4917),
    '충청남도': (36.5184, 126.8000),
    '전라북도': (35.7167, 127.1441),
    '전라남도': (34.8161, 126.4629),
    '경상북도': (36.4919, 128.8889),
    '경상남도': (35.4606, 128.2132),
    '제주특별자치도': (33.4996, 126.5312)
}

# CSV 업로더
uploaded_file = st.file_uploader("CSV 파일을 업로드해주세요 (EUC-KR 인코딩)", type="csv")

if uploaded_file:
    # CSV 읽기
    df = pd.read_csv(uploaded_file, encoding='euc-kr')

    # 컬럼 자동 추출
    region_col = [col for col in df.columns if '행정구역' in col][0]
    total_pop_col = [col for col in df.columns if "총인구수" in col][0]

    # 전처리: 괄호 제거 + 시·도만 추출
    df[region_col] = df[region_col].str.replace(r"\(.*\)", "", regex=True).str.strip()
    df[region_col] = df[region_col].str.extract(r"^(\S+?[시도])")  # 예: '서울특별시 종로구' → '서울특별시'

    # 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    # 행정구역별 원 추가
    for _, row in df.iterrows():
        region = row[region_col]
        pop_raw = str(row[total_pop_col]).replace(",", "")
        pop = pd.to_numeric(pop_raw, errors='coerce')

        if pd.notnull(pop) and region in region_coords:
            lat, lon = region_coords[region]

            folium.CircleMarker(
                location=(lat, lon),
                radius=max(5, min(pop / 50000, 30)),
                color='pink',
                fill=True,
                fill_color='pink',
                fill_opacity=0.5,
                popup=f"{region} : {int(pop):,}명"
            ).add_to(m)

    # 지도 출력
    st.subheader("행정구역별 인구 시각화 지도")
    st_data = st_folium(m, width=900, height=600)

    st.caption("※ 행정구역 중심 좌표 기준으로 원을 표시합니다. 정확한 행정 경계는 포함되지 않습니다.")
else:
    st.info("CSV 파일을 업로드하면 인구 지도가 표시됩니다.")

