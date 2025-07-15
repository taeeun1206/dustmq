import streamlit as st
st.title('내 최애 아이스크림 맛 선택!!')
name = st.text_input('이름을 입력해주세요 : ')
menu = st.selectbox('좋아하는 맛을 선택해주세요:', ['망고빙수','아몬드봉봉','뉴욕치즈케이크'.'요거트','슈팅스타','엄마는 외계인','그린티'])
if st.button('인사말 생성') : 
  st.write(name+'님! 당신이 좋아하는 음식은 '+menu+'이군요?! 저도 좋아요!!')
