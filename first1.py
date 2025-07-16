import streamlit as st
import pandas as pd

# 파일 경로 (Streamlit 앱과 같은 폴더에 CSV 파일 위치해야 함)
FILE_PATH = '202505_202505_연령별인구현황_월간.csv'

# EUC-KR 인코딩으로 데이터 읽기
df = pd.read_csv(FILE_PATH, encoding='euc-kr')

# 열 이름 중 '2025년05월_계_'로 시작하는 컬럼만 선택
age_cols = [col for col in df.columns if col.startswith('2025년05월_계_')]
# 연령 숫자만 추출 (예: '2025년05월_계_0세' → '0')
age_labels = [col.split('_')[-1].replace('세', '') for col in age_cols]

# 연령별 인구 데이터만 추출
age_df = df[['행정구역', '총인구수'] + age_cols].copy()
age_df.columns = ['행정구역', '총인구수'] + age_labels  # 연령 컬럼 이름 간단히

# 총인구수 기준 상위 5개 지역만 추출
top5_df = age_df.sort_values(by='총인구수', ascending=False).head(5)

# Streamlit 앱 구성
st.title("2025년 5월 기준 연령별 인구 분석")
st.subheader("총인구수 상위 5개 행정구역의 연령별 인구 현황")

# 연령별 인구 시각화
st.write("### 연령별 인구 분포 (단위: 명)")
top5_age_only = top5_df.set_index('행정구역').drop(columns='총인구수')
# Transpose 해서 연령이 인덱스(세로축), 지역이 열
st.line_chart(top5_age_only.T)

# 원본 데이터 보여주기
st.write("### 원본 데이터 (상위 5개 행정구역 기준)")
st.dataframe(top5_df)
