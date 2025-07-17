import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("2025년 5월 기준 연령별 인구 현황 분석 및 지도 시각화")

# 행정구역 중심 좌표 (시도 단위, 필요하면 확장)
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

    region_col = [col for col in df.columns if '행정구역' in col][0]
    age_columns = [col for col in df.columns if col.startswith("2025년05월_계_") and "세" in col]
    total_pop_col = [col for col in df.columns if "총인구수" in col][0]

    # 괄호 제거 및 시도명만 추출 (ex: 서울특별시 종로구 → 서울특별시)
    df[region_col] = df[region_col].str.replace(r"\(.*\)", "", regex=True).str.strip()
    df[region_col] = df[region_col].str.extract(r"^(\S+?[시도])")[0]

    age_labels = [col.replace("2025년05월_계_", "").replace("세", "") for col in age_columns]
    df_age = df[[region_col, total_pop_col] + age_columns].copy()
    rename_dict = dict(zip(age_columns, age_labels))
    df_age.rename(columns=rename_dict, inplace=True)

    df_top5 = df_age.sort_values(by=total_pop_col, ascending=False).head(5)

    tab1, tab2, tab3 = st.tabs(["기본 분석", "지역 선택 분석", "지도 시각화"])

    with tab1:
        st.subheader("원본 데이터 미리보기")
        st.dataframe(df)

        st.subheader("총인구수 기준 상위 5개 지역")
        st.dataframe(df_top5[[region_col, total_pop_col]])

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

        st.subheader("총인구수 상위 5개 지역 연령별 인구 선 그래프")
        st.line_chart(df_plot)

    with tab2:
        st.subheader("그래프로 보고 싶은 지역을 선택하세요")
        regions = df_age[region_col].unique().tolist()
        selected_regions = st.multiselect("지역 선택", options=regions, default=df_top5[region_col].tolist())

        if selected_regions:
            df_selected = df_age[df_age[region_col].isin(selected_regions)].copy()

            for col in age_only_cols:
                df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')

            st.subheader("선택한 지역의 총인구수")
            st.dataframe(df_selected[[region_col, total_pop_col]].sort_values(by=total_pop_col, ascending=False))

            age_bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 150]
            age_labels_bins = ['10살 미만', '10대', '20대', '30대', '40대', '50대',
                               '60대', '70대', '80대', '90대', '100대 이상']

            age_data = df_selected[age_only_cols].copy()
            age_data_cols_int = []
            for col in age_data.columns:
                try:
                    age_data_cols_int.append(int(col))
                except:
                    pass

            age_data = age_data[list(map(str, age_data_cols_int))]
            age_data.columns = age_data_cols_int

            df_agegroup_sum = pd.DataFrame()
            for idx, row in age_data.iterrows():
                s = pd.Series(row.values, index=age_data.columns)
                s = s.groupby(pd.cut(s.index, bins=age_bins, labels=age_labels_bins)).sum()
                df_agegroup_sum = pd.concat([df_agegroup_sum, s], axis=1)

            df_agegroup_sum = df_agegroup_sum.T
            df_agegroup_sum.index = df_selected[region_col].values

            st.subheader("선택한 지역의 연령대별 인구 합계")
            st.dataframe(df_agegroup_sum)

            st.subheader("선택한 지역의 연령별 인구 선 그래프")
            df_plot2 = df_selected[[region_col] + age_only_cols].set_index(region_col).T
            df_plot2.index.name = '연령'
            df_plot2 = df_plot2[df_plot2.index.str.match(r'^\d+$')]
            df_plot2.index = df_plot2.index.astype(int)
            df_plot2 = df_plot2.sort_index()
            df_plot2 = df_plot2.fillna(0)
            st.line_chart(df_plot2)

        else:
            st.warning("하나 이상의 지역을 선택해주세요.")

    with tab3:
        st.subheader("선택한 지역의 인구수 지도 시각화")

        selected_regions_map = st.multiselect("지도에 표시할 지역 선택", options=df_age[region_col].unique().tolist(), default=df_top5[region_col].tolist())

        if selected_regions_map:
            df_map = df_age[df_age[region_col].isin(selected_regions_map)].copy()

            m = folium.Map(location=[36.5, 127.5], zoom_start=7)

            for _, row in df_map.iterrows():
                region = row[region_col]
                pop = pd.to_numeric(row[total_pop_col], errors='coerce')
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

            st_data = st_folium(m, width=900, height=600)

        else:
            st.info("하나 이상의 지역을 선택해주세요.")
else:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")
