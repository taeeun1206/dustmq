import streamlit as st
import pandas as pd

# 제목
st.title("2025년 5월 기준 연령별 인구 현황")
st.write("상위 5개 행정구역의 연령별 인구수를 시각화한 결과입니다.")

# CSV 읽기
df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="euc-kr")

# 전처리
df['총인구수'] = df['2025년05월_계_총인구수'].str.replace(',', '').astype(int)

# 연령 관련 열 추출 및 이름 정리
age_columns = [col for col in df.columns if col.startswith('2025년05월_계_') and '세' in col]
age_column_mapping = {col: col.replace('2025년05월_계_', '') for col in age_columns}
df = df.rename(columns=age_column_mapping)

# 분석용 데이터프레임 구성
df_processed = df[['행정구역', '총인구수'] + list(age_column_mapping.values())]

# 총인구수 기준 상위 5개 행정구역 추출
top5 = df_processed.sort_values(by='총인구수', ascending=False).head(5)
top5_age = top5.set_index('행정구역').drop(columns=['총인구수']).T  # 연령을 세로축으로

# 선 그래프 시각화
st.subheader("상위 5개 행정구역의 연령별 인구 분포")
st.line_chart(top5_age)

# 원본 데이터 출력
st.subheader("원본 데이터 (전처리됨)")
st.dataframe(df_processed)
