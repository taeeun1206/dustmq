import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("2025년 5월 기준 연령별 인구 현황 분석")

# 지도 표시를 위한 행정구역별 위경도 정보 (예시)
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

uploaded_file = st.file_uploader("CSV 파일을 업로드해주세요 (EUC-KR 인코딩)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='euc-kr')

    st.subheader("원본 데이터 미리보기")
    st.dataframe(df)

    region_col = [col for col in df.columns if '행정구역' in col][0]
    age_columns = [col for col in df.columns if col.startswith("2025년05월_계_") and "세" in col]
    total_pop_col = [col for col in df.columns if "총인구수" in col][0]

    # 행정구역명 괄호 제거 (예: "서울특별시(11)" → "서울특별시")
    df[region_col] = df[region_col].str.replace(r"\(.*\)", "", regex=True).str.strip()

    age_labels = [col.replace("2025년05월_계_", "").replace("세", "") for col in age_columns]
    df_age = df[[region_col, total_pop_col] + age_columns].copy()
    rename_dict = dict(zip(age_columns, age_labels))
    df_age.rename(columns=rename_dict, inplace=True)

    df_top5 = df_age.sort_values(by=total_pop_col, ascending=False).head(5)

    st.subheader("총인구수 기준 상위 5개 지역")
    st.dataframe(df_top5[[region_col, total_pop_col]])

    # 연령별 인구 선 그래프
    age_only_cols = age_labels
    df_plot = df_top5[[region_col] + age_only_cols].copy()
    for col in age_only_cols:
        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')

    df_plot = df_plot.set_index(region_col).T
    df_plot.index.name = '연령'
    df_plot = df_plot[df_plot.index.str.match(r'^\d+$')]
    df_plot.index = df_plot.index.astype(int)
    df_plot = df_plot.sort_index()
    df_plot = df_plot.fillna(0)

    st.subheader("연령별 인구 선 그래프 (상위 5개 지역)")
    st.line_chart(df_plot)

    st.subheader("행정구역별 인구 분포 지도")

    # folium 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    for _, row in df_age.iterrows():
        region = row[region_col]
        pop = row[total_pop_col]

        # 위경도가 존재하는 지역만 표시
        if region in region_coords:
            lat, lon = region_coords[region]

            folium.CircleMarker(
                location=(lat, lon),
                radius=max(5, min(pop / 50000, 30)),  # 인구수에 따라 원 크기 조절
                color='pink',
                fill=True,
                fill_opacity=0.5,
                fill_color='pink',
                popup=f"{region} : {pop:,}명"
            ).add_to(m)

    # 지도 표시
    st_data = st_folium(m, width=900, height=600)

    st.caption("지도 좌표는 지역 중심 좌표 기준입니다. 정확한 행정구역 경계와는 다를 수 있습니다.")
else:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")

