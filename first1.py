import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("2025년 5월 기준 연령별 인구 현황 - 지도 표시")

uploaded_file = st.file_uploader("CSV 파일을 업로드해주세요 (EUC-KR 인코딩)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='euc-kr')

    st.subheader("원본 데이터 미리보기")
    st.dataframe(df)

    # 컬럼 자동 추출
    region_col = [col for col in df.columns if '행정구역' in col][0]
    total_pop_col = [col for col in df.columns if "총인구수" in col][0]

    # 총인구수 상위 5개 지역 추출
    df_top5 = df.sort_values(by=total_pop_col, ascending=False).head(5)

    st.subheader("총인구수 기준 상위 5개 지역")
    st.dataframe(df_top5[[region_col, total_pop_col]])

    # 행정구역별 좌표 (예시: 실제 좌표는 직접 추가해야 함)
    # 최소 5개 지역만 표시용 좌표 예시로 넣음 (서울, 부산, 인천, 대구, 광주)
    region_coords = {
        "서울특별시": [37.5665, 126.9780],
        "부산광역시": [35.1796, 129.0756],
        "인천광역시": [37.4563, 126.7052],
        "대구광역시": [35.8722, 128.6025],
        "광주광역시": [35.1595, 126.8526],
    }

    # folium 지도 생성 (대한민국 중심 좌표 및 적절한 확대 레벨)
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    # 상위 5개 지역 마커 추가
    for idx, row in df_top5.iterrows():
        region = row[region_col]
        pop = row[total_pop_col]

        # 좌표 있으면 마커 표시
        if region in region_coords:
            lat, lon = region_coords[region]
            # CircleMarker: 반투명 원형 마커
            folium.CircleMarker(
                location=[lat, lon],
                radius=pop / 1000000,  # 인구수 크기에 비례 (조절 가능)
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.4,   # 반투명
                popup=f"{region} - 총인구수: {pop:,}"
            ).add_to(m)
        else:
            st.warning(f"'{region}' 지역 좌표 정보가 없어 지도에 표시할 수 없습니다.")

    st.subheader("지도에서 상위 5개 지역 인구 표시")
    st_folium(m, width=700, height=500)

else:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")
