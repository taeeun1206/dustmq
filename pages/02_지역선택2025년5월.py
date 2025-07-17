import streamlit as st
import pandas as pd

st.title("2025년 5월 기준 연령별 인구 현황 분석")

uploaded_file = st.file_uploader("CSV 파일을 업로드해주세요 (EUC-KR 인코딩)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='euc-kr')

    region_col = [col for col in df.columns if '행정구역' in col][0]
    age_columns = [col for col in df.columns if col.startswith("2025년05월_계_") and "세" in col]
    total_pop_col = [col for col in df.columns if "총인구수" in col][0]

    age_labels = [col.replace("2025년05월_계_", "").replace("세", "") for col in age_columns]
    df_age = df[[region_col, total_pop_col] + age_columns].copy()
    rename_dict = dict(zip(age_columns, age_labels))
    df_age.rename(columns=rename_dict, inplace=True)

    df_top5 = df_age.sort_values(by=total_pop_col, ascending=False).head(5)

    tab1, tab2 = st.tabs(["기본 분석", "지역 선택 분석"])

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

            # 1. 총인구수 표
            st.subheader("선택한 지역의 총인구수")
            st.dataframe(df_selected[[region_col, total_pop_col]].sort_values(by=total_pop_col, ascending=False))

            # 2. 연령대별 인구 합계 계산 및 표
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

            # 3. 연령별 인구 선 그래프
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

else:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")
