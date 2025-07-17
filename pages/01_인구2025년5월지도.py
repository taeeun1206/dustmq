import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("2025년 5월 기준 상위 5개 행정구역 인구 지도")

# 중심 좌표 (행정구역명 → 위도/경도)
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

    # 전처리: 괄호 제거 + 시·도 추출
    df[region_col] = df[region_col].str.replace(r"\(.*\)", "", regex=True).str.strip()
    df[region_col] = df[region_col].str.extract(r"^(\S+?[시도])")

    # 총인구수 정수형 변환
    df[total_pop_col] = df[total_pop_col].astype(str).str.replace(",", "")
    df[total_pop_col] = pd.to_numeric(df[total_pop_col], errors="coerce")

    # 유효한 좌표 있는 지역만 필터링
    df = df[df[region_col].isin(region_coords.keys())]

    # 상위 5개 지역만 선택
    df_top5 = df.sort_values(by=total_pop_col, ascending=False).head(5)

    # 최대값 (원 크기 정규화용)
    max_pop = df_top5[total_pop_col].max()

    # 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    for _, row in df_top5.iterrows():
        region = row[region_col]
        pop = row[total_pop_col]
        lat, lon = region_coords[region]

        # 원 크기 정규화
        radius = (pop / max_pop) * 30  # 최대 반지름 30

        folium.CircleMarker(
            location=(lat, lon),
            radius=radius,
            color='pink',
            fill=True,
            fill_color='pink',
            fill_opacity=0.5,
            popup=f"{region} : {int(pop):,}명"
        ).add_to(m)

    # 지도 출력
    st.subheader("총인구수 상위 5개 행정구역 지도 시각화")
    st_data = st_folium(m, width=900, height=600)

    st.caption("※ 원 크기는 총인구수 기준 상대적으로 나타냅니다. 정확한 위치는 중심 좌표 기준입니다.")
else:
    st.info("CSV 파일을 업로드하면 상위 5개 행정구역의 인구 지도가 표시됩니다.")
