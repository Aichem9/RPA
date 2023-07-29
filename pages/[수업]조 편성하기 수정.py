import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import pandas as pd
import random
from faker import Faker

st.title("특성을 바탕으로 조 편성하기🤼‍♂️")

st.info('###### 언제 사용하나요?\n몇개의 번호 중에서 여러 번호를 추첨할 때! ')
st.warning('###### 어떻게 해결하나요?\n학생 데이터를 업로드하여 특성 고려한 편성')
# seed를 고정시키는 코드
seed = 1234

fake = Faker('ko_KR')
fake.seed_instance(seed)  # faker의 난수를 고정합니다.

# n명의 자료 생성하기
def generate_names_faker(n):
    names = []
    for _ in range(n):
        name = fake.name()
        names.append(name)
    return names

# n명을 k개 그룹으로 나눌 때 조별 인원수 리스트
def divide_n_into_k_parts(n, k):
    quotient = n // k
    remainder = n % k

    sizes = [quotient] * k
    for i in range(remainder):
        sizes[i] += 1

    intervals = []
    start = 0
    for size in sizes:
        end = start + size
        intervals.append(size)
        start = end
    return intervals 

def random_group(df, k):
    n = len(df)
    # 인원수 리스트 생성
    
    # 랜덤 셔플
    sample_random = df.sample(frac=1).reset_index(drop=True)
    # 그룹 부여
    sample_random['group'] = 0
    # 리스트 nb_of_st_list를 사용하여 'group' 열에 값을 할당
    start = 0
    nb_of_st_list = divide_n_into_k_parts(n, k)

    for i, nb in enumerate(nb_of_st_list):
        end = start + nb
        sample_random.loc[start:end-1, 'group'] = i + 1
        start = end
    return sample_random

def grouping(df, k):
    # 라디오 버튼 선택에 따른 코드 실행
    selected_option = st.radio("옵션 선택", ['랜덤', '범주'])

    if selected_option == '랜덤':
        if st.button('편성하기'):
            st.write('랜덤으로 모둠을 편성합니다.')
            n = len(df)
            # 랜덤 셔플
            sample_random = df.sample(frac=1).reset_index(drop=True)
            # 그룹 부여
            sample_random['group'] = 0
            # 리스트 nb_of_st_list를 사용하여 'group' 열에 값을 할당
            start = 0
            nb_of_st_list = divide_n_into_k_parts(n, k)
            for i, nb in enumerate(nb_of_st_list):
                end = start + nb
                sample_random.loc[start:end-1, 'group'] = i + 1
                start = end
            st.write(sample_random)

    elif selected_option == '수치':
        col = st.text_input('기준이 되는 열 이름을 입력해주세요("점수"):', value='점수')
        st.write(col, '(을/를) 고려하여 학생을 모둠별로 편성한 결과를 보려면 아래 버튼을 클릭해주세요. ')
        if st.button('편성하기'):
            # 수치 편성 코드
            # ...
            st.write('준비중입니다. ')

    elif selected_option == '범주':
        col = st.selectbox('기준이 되는 열 이름을 선택해주세요', ['특성', '에너지'])
        st.write(col, '(을/를) 고려하여 학생을 모둠별로 편성한 결과를 보려면 아래 버튼을 클릭해주세요. ')
        if st.button('편성하기'):
            # 범주 편성 코드
            categorical_data_grouping(df, col)#, epsilon_sum, epsilon_std)

def categorical_data_grouping(df, col):#, epsilon_sum, epsilon_std):

    one_hot_encoded = pd.get_dummies(df[col], prefix=col)
    categories = one_hot_encoded.columns
    df_encoded = pd.concat([df, one_hot_encoded], axis=1)
    df_group = random_group(df_encoded, k) #초기값, 임의로 그룹핑된 상태
    st.write("### 임의 그룹핑")
    st.write(df_group)
    def calculate_group_std_sum_and_std(df_group):
        group_stds = []
        for i in range(k):#그룹 개수만큼 반복문
            group_data = df_group[df_group['group'] == i+1][categories]  # 해당 그룹의 데이터 선택
            # st.write(group_data)
            group_std = group_data.sum().std()  # 그룹의 표준편차 계산
            group_stds.append(group_std)
        return group_stds, df_group

    df = df_group
    for i in range(100):
        group_stds, df = calculate_group_std_sum_and_std(df)

        # 임의의 두 그룹 선택
        group_list = df.group.unique()
        g1, g2 = random.sample(group_list.tolist(),2)

        df1 = df[df.group==g1]
        df2 = df[df.group==g2]

        p1 = random.sample(df1.index.tolist(), 1)
        p2 = random.sample(df2.index.tolist(), 1)

        df.loc[p1, 'group'] = g2
        df.loc[p2, 'group'] = g1

        # 새로운 a, b, c 계산
        new_group_stds, new_df = calculate_group_std_sum_and_std(df)

        if np.sum(new_group_stds) < np.sum(group_stds):
            # st.write('update...', np.sum(group_stds), np.sum(new_group_stds))
            # st.write(group_stds, new_group_stds)
            df = new_df
        else:
            df = df
        #st.write(df)

    st.write('### 트레이딩 후')
    st.write(df)
    group_stds, df = calculate_group_std_sum_and_std(df)
    st.write(group_stds)

    


sample_checked = st.checkbox('샘플 파일 조 편성하기')
# 샘플 데이터 생성
n_students = int(st.text_input('샘플 데이터를 생성합니다. 학생 수를 설정해주세요:', value = 30))
k = int(st.text_input('모둠 수를 입력하세요:', value=8)) # 그룹의 개수


names = generate_names_faker(n_students)
scores = np.round(np.random.normal(loc=55, scale=18, size=n_students))
scores = np.clip(scores, 0, 100)
grades = np.random.choice(['A', 'B', 'C', 'D'], size=n_students, p=[0.3, 0.3, 0.2, 0.2])
energy = np.random.choice(['E','I'], size=n_students, p=[0.5, 0.5])
data = {'이름': names, '점수': scores, '특성': grades, '에너지': energy}
sample_data = pd.DataFrame(data)

if 'student_data' not in st.session_state:
    st.session_state['student_data'] = ''

if sample_checked:
    with st.spinner('조 편성 중 ...'):
        st.write('???')
        
        grouping(sample_data, k)



student_data = st.file_uploader("학생 데이터 csv 파일을 업로드해주세요! 준비된 파일이 없을 경우, 아래 '샘플 파일 업로드 해보기' 버튼을 눌러 테스트해보세요.", type="csv")

if student_data:
    student_data = pd.read_csv(student_data, encoding = 'utf-8')
    st.session_state['student_data'] = student_data

upload_checked = st.checkbox('업로드한 파일 조 편성하기!')
if upload_checked:
    st.write(student_data.head(5))
    with st.spinner('조 편성 중...'):
        try:
            k = int(st.text_input('모둠 수를 입력하세요:', value=8)) # 그룹의 개수
            grouping(student_data, k)
        except:
            st.write("⚠올바른 파일을 업로드하셨는지 확인해주세요!")
