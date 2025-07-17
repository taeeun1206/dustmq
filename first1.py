import streamlit as st
import pandas as pd

st.title("2025년 5월 기준 연령별 인구 현황 분석")

# CSV 파일 업로더
uploaded_file = st.file_uploader("CSV 파일을 업로드해주세요 (EUC-KR 인코딩)", type="csv")

if uploaded_file:
    # CSV 파일 읽기
    df = pd.read_csv(uploaded_file, encoding='euc-kr')

    st.subheader("원본 데이터 미리보기")
    st.dataframe(df)

    # 행정구역, 연령별 인구, 총인구수 컬럼 추출
    region_col = [col for col in df.columns if '행정구역' in col][0]
    age_columns = [col for col in df.columns if col.startswith("2025년05월_계_") and "세" in col]
    total_pop_col = [col for col in df.columns if "총인구수" in col][0]

    # 연령 숫자만 추출하여 열 이름 바꾸기
    age_labels = [col.replace("2025년05월_계_", "").replace("세", "") for col in age_columns]
    df_age = df[[region_col, total_pop_col] + age_columns].copy()
    rename_dict = dict(zip(age_columns, age_labels))
    df_age.rename(columns=rename_dict, inplace=True)

    # 총인구수 기준 상위 5개 지역 추출
    df_top5 = df_age.sort_values(by=total_pop_col, ascending=False).head(5)

    st.subheader("총인구수 기준 상위 5개 지역")
    st.dataframe(df_top5[[region_col, total_pop_col]])

    # 연령별 인구 데이터만 추출하고 숫자형으로 변환
    age_only_cols = age_labels
    df_plot = df_top5[[region_col] + age_only_cols].copy()
    for col in age_only_cols:
        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')

    # 인덱스 설정 및 전치
    df_plot = df_plot.set_index(region_col).T

    # 인덱스(연령)가 숫자인 값만 선택
    df_plot.index.name = '연령'
    df_plot = df_plot[df_plot.index.str.match(r'^\d+$')]
    df_plot.index = df_plot.index.astype(int)
    df_plot = df_plot.sort_index()

    # 선 그래프 시각화
    st.subheader("연령별 인구 선 그래프")
    st.line_chart(df_plot)

    st.caption("데이터 출처: 통계청")
else:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")
